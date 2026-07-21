"""
Testes unitários do módulo Bankroll Statistics.

Este arquivo valida:

- criação e imutabilidade da fotografia estatística;
- normalização e proteção do ledger;
- validação dos saldos;
- agregação de depósitos, saques e ajustes;
- contagem de WIN, LOSS e DRAW;
- cálculo das taxas operacionais;
- cálculo de stakes;
- lucro realizado;
- ROI;
- exposição da banca;
- agrupamento de operações por contrato.
"""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable
from uuid import UUID, uuid4

from src.bankroll.enums import (
    BankrollEntryStatus,
    BankrollTransactionDirection,
    BankrollTransactionType,
)
from src.bankroll.statistics import BankrollStatistics
from src.bankroll.transaction import BankrollTransaction


ZERO = Decimal("0")


class TestBankrollStatistics(unittest.TestCase):
    """Testa a fotografia estatística imutável da banca."""

    def test_should_create_empty_statistics(self) -> None:
        """Deve criar uma fotografia estatística vazia."""

        statistics = BankrollStatistics()

        self.assertEqual(statistics.ledger, ())
        self.assertEqual(statistics.available_balance, ZERO)
        self.assertEqual(statistics.reserved_balance, ZERO)
        self.assertEqual(statistics.total_balance, ZERO)
        self.assertEqual(statistics.total_operations, 0)

    def test_should_use_slots(self) -> None:
        """Deve utilizar slots e não possuir __dict__."""

        statistics = BankrollStatistics()

        self.assertFalse(hasattr(statistics, "__dict__"))

    def test_should_be_immutable(self) -> None:
        """Deve impedir alteração dos campos após a criação."""

        statistics = BankrollStatistics(
            available_balance=Decimal("100"),
        )

        with self.assertRaises(FrozenInstanceError):
            statistics.available_balance = Decimal("200")  # type: ignore[misc]

    def test_should_convert_ledger_to_tuple(self) -> None:
        """Deve converter o ledger recebido para uma tuple."""

        transaction = self._create_transaction(
            transaction_type=BankrollTransactionType.DEPOSIT,
            direction=BankrollTransactionDirection.CREDIT,
            amount=Decimal("100"),
        )

        statistics = BankrollStatistics(ledger=[transaction])

        self.assertIsInstance(statistics.ledger, tuple)
        self.assertEqual(statistics.ledger, (transaction,))

    def test_should_accept_generator_as_ledger(self) -> None:
        """Deve aceitar um gerador de transações como ledger."""

        transaction = self._create_transaction(
            transaction_type=BankrollTransactionType.DEPOSIT,
            direction=BankrollTransactionDirection.CREDIT,
            amount=Decimal("100"),
        )

        ledger = self._create_generator([transaction])

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(statistics.ledger, (transaction,))

    def test_should_create_snapshot_of_original_collection(self) -> None:
        """
        Alterações na coleção original não devem modificar a fotografia.
        """

        first_transaction = self._create_transaction(
            transaction_type=BankrollTransactionType.DEPOSIT,
            direction=BankrollTransactionDirection.CREDIT,
            amount=Decimal("100"),
        )
        second_transaction = self._create_transaction(
            transaction_type=BankrollTransactionType.DEPOSIT,
            direction=BankrollTransactionDirection.CREDIT,
            amount=Decimal("200"),
        )

        original_ledger = [first_transaction]

        statistics = BankrollStatistics(ledger=original_ledger)

        original_ledger.append(second_transaction)

        self.assertEqual(statistics.ledger, (first_transaction,))
        self.assertEqual(statistics.total_deposits, Decimal("100"))

    def test_should_reject_string_as_ledger(self) -> None:
        """Deve rejeitar texto utilizado como ledger."""

        with self.assertRaisesRegex(
            TypeError,
            "ledger must be an iterable",
        ):
            BankrollStatistics(ledger="invalid ledger")

    def test_should_reject_non_iterable_ledger(self) -> None:
        """Deve rejeitar um objeto não iterável como ledger."""

        with self.assertRaisesRegex(
            TypeError,
            "ledger must be an iterable",
        ):
            BankrollStatistics(ledger=123)  # type: ignore[arg-type]

    def test_should_reject_invalid_ledger_item(self) -> None:
        """Deve rejeitar elementos que não sejam transações."""

        with self.assertRaisesRegex(
            TypeError,
            "Every ledger item must be",
        ):
            BankrollStatistics(
                ledger=[object()],  # type: ignore[list-item]
            )

    def test_should_reject_non_decimal_available_balance(self) -> None:
        """Deve rejeitar saldo disponível que não seja Decimal."""

        with self.assertRaisesRegex(
            TypeError,
            "available_balance must be a Decimal",
        ):
            BankrollStatistics(
                available_balance=100,  # type: ignore[arg-type]
            )

    def test_should_reject_non_decimal_reserved_balance(self) -> None:
        """Deve rejeitar saldo reservado que não seja Decimal."""

        with self.assertRaisesRegex(
            TypeError,
            "reserved_balance must be a Decimal",
        ):
            BankrollStatistics(
                reserved_balance=50,  # type: ignore[arg-type]
            )

    def test_should_reject_negative_available_balance(self) -> None:
        """Deve rejeitar saldo disponível negativo."""

        with self.assertRaisesRegex(
            ValueError,
            "available_balance cannot be negative",
        ):
            BankrollStatistics(
                available_balance=Decimal("-0.01"),
            )

    def test_should_reject_negative_reserved_balance(self) -> None:
        """Deve rejeitar saldo reservado negativo."""

        with self.assertRaisesRegex(
            ValueError,
            "reserved_balance cannot be negative",
        ):
            BankrollStatistics(
                reserved_balance=Decimal("-0.01"),
            )

    def test_should_reject_nan_available_balance(self) -> None:
        """Deve rejeitar saldo disponível NaN."""

        with self.assertRaisesRegex(
            ValueError,
            "available_balance must be finite",
        ):
            BankrollStatistics(
                available_balance=Decimal("NaN"),
            )

    def test_should_reject_infinite_reserved_balance(self) -> None:
        """Deve rejeitar saldo reservado infinito."""

        with self.assertRaisesRegex(
            ValueError,
            "reserved_balance must be finite",
        ):
            BankrollStatistics(
                reserved_balance=Decimal("Infinity"),
            )

    def test_should_calculate_total_balance(self) -> None:
        """
        Saldo total deve somar saldo disponível e saldo reservado.
        """

        statistics = BankrollStatistics(
            available_balance=Decimal("850"),
            reserved_balance=Decimal("150"),
        )

        self.assertEqual(
            statistics.total_balance,
            Decimal("1000"),
        )

    def test_should_calculate_total_deposits(self) -> None:
        """Deve somar apenas as transações de depósito."""

        ledger = (
            self._create_transaction(
                transaction_type=BankrollTransactionType.DEPOSIT,
                direction=BankrollTransactionDirection.CREDIT,
                amount=Decimal("1000"),
            ),
            self._create_transaction(
                transaction_type=BankrollTransactionType.DEPOSIT,
                direction=BankrollTransactionDirection.CREDIT,
                amount=Decimal("500"),
            ),
            self._create_transaction(
                transaction_type=BankrollTransactionType.WITHDRAWAL,
                direction=BankrollTransactionDirection.DEBIT,
                amount=Decimal("200"),
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.total_deposits,
            Decimal("1500"),
        )

    def test_should_calculate_total_withdrawals(self) -> None:
        """Deve somar apenas as transações de saque."""

        ledger = (
            self._create_transaction(
                transaction_type=BankrollTransactionType.WITHDRAWAL,
                direction=BankrollTransactionDirection.DEBIT,
                amount=Decimal("100"),
            ),
            self._create_transaction(
                transaction_type=BankrollTransactionType.WITHDRAWAL,
                direction=BankrollTransactionDirection.DEBIT,
                amount=Decimal("250"),
            ),
            self._create_transaction(
                transaction_type=BankrollTransactionType.DEPOSIT,
                direction=BankrollTransactionDirection.CREDIT,
                amount=Decimal("1000"),
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.total_withdrawals,
            Decimal("350"),
        )

    def test_should_calculate_net_cash_flow(self) -> None:
        """Fluxo líquido deve ser depósitos menos saques."""

        ledger = (
            self._create_transaction(
                transaction_type=BankrollTransactionType.DEPOSIT,
                direction=BankrollTransactionDirection.CREDIT,
                amount=Decimal("2000"),
            ),
            self._create_transaction(
                transaction_type=BankrollTransactionType.WITHDRAWAL,
                direction=BankrollTransactionDirection.DEBIT,
                amount=Decimal("450"),
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.net_cash_flow,
            Decimal("1550"),
        )

    def test_should_calculate_credit_adjustments(self) -> None:
        """Deve somar os ajustes administrativos de crédito."""

        ledger = (
            self._create_transaction(
                transaction_type=(
                    BankrollTransactionType.CREDIT_ADJUSTMENT
                ),
                direction=BankrollTransactionDirection.CREDIT,
                amount=Decimal("20"),
            ),
            self._create_transaction(
                transaction_type=(
                    BankrollTransactionType.CREDIT_ADJUSTMENT
                ),
                direction=BankrollTransactionDirection.CREDIT,
                amount=Decimal("30"),
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.credit_adjustments,
            Decimal("50"),
        )

    def test_should_calculate_debit_adjustments(self) -> None:
        """Deve somar os ajustes administrativos de débito."""

        ledger = (
            self._create_transaction(
                transaction_type=(
                    BankrollTransactionType.DEBIT_ADJUSTMENT
                ),
                direction=BankrollTransactionDirection.DEBIT,
                amount=Decimal("12"),
            ),
            self._create_transaction(
                transaction_type=(
                    BankrollTransactionType.DEBIT_ADJUSTMENT
                ),
                direction=BankrollTransactionDirection.DEBIT,
                amount=Decimal("8"),
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.debit_adjustments,
            Decimal("20"),
        )

    def test_should_calculate_net_adjustments(self) -> None:
        """
        Ajuste líquido deve ser créditos de ajuste menos débitos.
        """

        ledger = (
            self._create_transaction(
                transaction_type=(
                    BankrollTransactionType.CREDIT_ADJUSTMENT
                ),
                direction=BankrollTransactionDirection.CREDIT,
                amount=Decimal("50"),
            ),
            self._create_transaction(
                transaction_type=(
                    BankrollTransactionType.DEBIT_ADJUSTMENT
                ),
                direction=BankrollTransactionDirection.DEBIT,
                amount=Decimal("15"),
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.net_adjustments,
            Decimal("35"),
        )

    def test_should_calculate_total_stake_reserved(self) -> None:
        """Deve somar o volume histórico de stakes reservadas."""

        first_contract_id = uuid4()
        second_contract_id = uuid4()

        ledger = (
            self._create_stake_reservation(
                amount=Decimal("100"),
                contract_id=first_contract_id,
            ),
            self._create_stake_reservation(
                amount=Decimal("150"),
                contract_id=second_contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.total_stake_reserved,
            Decimal("250"),
        )

    def test_should_calculate_total_stake_released(self) -> None:
        """Deve somar o volume histórico de stakes liberadas."""

        first_contract_id = uuid4()
        second_contract_id = uuid4()

        ledger = (
            self._create_transaction(
                transaction_type=(
                    BankrollTransactionType.STAKE_RELEASED
                ),
                direction=BankrollTransactionDirection.CREDIT,
                amount=Decimal("100"),
                contract_id=first_contract_id,
            ),
            self._create_transaction(
                transaction_type=(
                    BankrollTransactionType.STAKE_RELEASED
                ),
                direction=BankrollTransactionDirection.CREDIT,
                amount=Decimal("80"),
                contract_id=second_contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.total_stake_released,
            Decimal("180"),
        )

    def test_should_calculate_win_returns(self) -> None:
        """Deve somar os retornos brutos das operações WIN."""

        first_contract_id = uuid4()
        second_contract_id = uuid4()

        ledger = (
            self._create_win_settlement(
                amount=Decimal("180"),
                contract_id=first_contract_id,
            ),
            self._create_win_settlement(
                amount=Decimal("90"),
                contract_id=second_contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.total_win_returns,
            Decimal("270"),
        )

    def test_should_calculate_draw_returns(self) -> None:
        """Deve somar os valores devolvidos em operações DRAW."""

        first_contract_id = uuid4()
        second_contract_id = uuid4()

        ledger = (
            self._create_draw_settlement(
                amount=Decimal("100"),
                contract_id=first_contract_id,
            ),
            self._create_draw_settlement(
                amount=Decimal("50"),
                contract_id=second_contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.total_draw_returns,
            Decimal("150"),
        )

    def test_should_count_wins_losses_and_draws(self) -> None:
        """Deve contar corretamente os resultados operacionais."""

        win_contract_id = uuid4()
        loss_contract_id = uuid4()
        draw_contract_id = uuid4()

        ledger = (
            self._create_win_settlement(
                amount=Decimal("180"),
                contract_id=win_contract_id,
            ),
            self._create_win_settlement(
                amount=Decimal("90"),
                contract_id=uuid4(),
            ),
            self._create_loss_settlement(
                contract_id=loss_contract_id,
            ),
            self._create_draw_settlement(
                amount=Decimal("50"),
                contract_id=draw_contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(statistics.total_wins, 2)
        self.assertEqual(statistics.total_losses, 1)
        self.assertEqual(statistics.total_draws, 1)
        self.assertEqual(statistics.total_operations, 4)

    def test_should_return_zero_rates_without_operations(self) -> None:
        """Deve retornar taxas zero quando não houver liquidações."""

        statistics = BankrollStatistics()

        self.assertEqual(statistics.win_rate, ZERO)
        self.assertEqual(statistics.loss_rate, ZERO)
        self.assertEqual(statistics.draw_rate, ZERO)

    def test_should_calculate_operation_rates(self) -> None:
        """Deve calcular percentuais usando todas as liquidações."""

        ledger = (
            self._create_win_settlement(
                amount=Decimal("180"),
                contract_id=uuid4(),
            ),
            self._create_win_settlement(
                amount=Decimal("180"),
                contract_id=uuid4(),
            ),
            self._create_loss_settlement(
                contract_id=uuid4(),
            ),
            self._create_draw_settlement(
                amount=Decimal("100"),
                contract_id=uuid4(),
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.win_rate,
            Decimal("50"),
        )
        self.assertEqual(
            statistics.loss_rate,
            Decimal("25"),
        )
        self.assertEqual(
            statistics.draw_rate,
            Decimal("25"),
        )

    def test_should_return_zero_stake_metrics_without_reservations(
        self,
    ) -> None:
        """Deve retornar zero quando não houver stakes reservadas."""

        statistics = BankrollStatistics()

        self.assertEqual(statistics.average_stake, ZERO)
        self.assertEqual(statistics.max_stake, ZERO)
        self.assertEqual(statistics.min_stake, ZERO)
        self.assertEqual(statistics.total_stake_reserved, ZERO)

    def test_should_calculate_stake_metrics(self) -> None:
        """
        Deve calcular média, maior e menor stake corretamente.
        """

        ledger = (
            self._create_stake_reservation(
                amount=Decimal("50"),
                contract_id=uuid4(),
            ),
            self._create_stake_reservation(
                amount=Decimal("100"),
                contract_id=uuid4(),
            ),
            self._create_stake_reservation(
                amount=Decimal("150"),
                contract_id=uuid4(),
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.average_stake,
            Decimal("100"),
        )
        self.assertEqual(
            statistics.max_stake,
            Decimal("150"),
        )
        self.assertEqual(
            statistics.min_stake,
            Decimal("50"),
        )

    def test_should_accumulate_stakes_for_same_contract(self) -> None:
        """Deve acumular múltiplas reservas do mesmo contrato."""

        contract_id = uuid4()

        ledger = (
            self._create_stake_reservation(
                amount=Decimal("40"),
                contract_id=contract_id,
            ),
            self._create_stake_reservation(
                amount=Decimal("60"),
                contract_id=contract_id,
            ),
            self._create_win_settlement(
                amount=Decimal("180"),
                contract_id=contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.settled_stake,
            Decimal("100"),
        )
        self.assertEqual(
            statistics.realized_profit,
            Decimal("80"),
        )

    def test_should_calculate_settled_stake(self) -> None:
        """Deve considerar stakes apenas de contratos liquidados."""

        win_contract_id = uuid4()
        loss_contract_id = uuid4()
        open_contract_id = uuid4()

        ledger = (
            self._create_stake_reservation(
                amount=Decimal("100"),
                contract_id=win_contract_id,
            ),
            self._create_stake_reservation(
                amount=Decimal("80"),
                contract_id=loss_contract_id,
            ),
            self._create_stake_reservation(
                amount=Decimal("50"),
                contract_id=open_contract_id,
            ),
            self._create_win_settlement(
                amount=Decimal("180"),
                contract_id=win_contract_id,
            ),
            self._create_loss_settlement(
                contract_id=loss_contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.settled_stake,
            Decimal("180"),
        )

    def test_should_calculate_win_realized_profit(self) -> None:
        """WIN deve gerar retorno menos stake como lucro."""

        contract_id = uuid4()

        ledger = (
            self._create_stake_reservation(
                amount=Decimal("100"),
                contract_id=contract_id,
            ),
            self._create_win_settlement(
                amount=Decimal("180"),
                contract_id=contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.realized_profit,
            Decimal("80"),
        )

    def test_should_calculate_loss_realized_profit(self) -> None:
        """LOSS deve gerar prejuízo igual ao valor da stake."""

        contract_id = uuid4()

        ledger = (
            self._create_stake_reservation(
                amount=Decimal("100"),
                contract_id=contract_id,
            ),
            self._create_loss_settlement(
                contract_id=contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.realized_profit,
            Decimal("-100"),
        )

    def test_should_calculate_draw_realized_profit(self) -> None:
        """DRAW integral deve produzir resultado realizado zero."""

        contract_id = uuid4()

        ledger = (
            self._create_stake_reservation(
                amount=Decimal("100"),
                contract_id=contract_id,
            ),
            self._create_draw_settlement(
                amount=Decimal("100"),
                contract_id=contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.realized_profit,
            ZERO,
        )

    def test_should_calculate_combined_realized_profit(self) -> None:
        """Deve agregar WIN, LOSS e DRAW corretamente."""

        win_contract_id = uuid4()
        loss_contract_id = uuid4()
        draw_contract_id = uuid4()

        ledger = (
            self._create_stake_reservation(
                amount=Decimal("100"),
                contract_id=win_contract_id,
            ),
            self._create_win_settlement(
                amount=Decimal("180"),
                contract_id=win_contract_id,
            ),
            self._create_stake_reservation(
                amount=Decimal("100"),
                contract_id=loss_contract_id,
            ),
            self._create_loss_settlement(
                contract_id=loss_contract_id,
            ),
            self._create_stake_reservation(
                amount=Decimal("100"),
                contract_id=draw_contract_id,
            ),
            self._create_draw_settlement(
                amount=Decimal("100"),
                contract_id=draw_contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.realized_profit,
            Decimal("-20"),
        )

    def test_should_ignore_open_contract_in_realized_profit(self) -> None:
        """Contrato não liquidado não deve alterar lucro realizado."""

        contract_id = uuid4()

        ledger = (
            self._create_stake_reservation(
                amount=Decimal("100"),
                contract_id=contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(statistics.realized_profit, ZERO)
        self.assertEqual(statistics.settled_stake, ZERO)

    def test_should_process_only_first_settlement_per_contract(
        self,
    ) -> None:
        """
        Deve impedir que liquidações duplicadas alterem o resultado.
        """

        contract_id = uuid4()

        first_settlement = self._create_win_settlement(
            amount=Decimal("180"),
            contract_id=contract_id,
        )
        duplicate_settlement = self._create_win_settlement(
            amount=Decimal("180"),
            contract_id=contract_id,
        )

        ledger = (
            self._create_stake_reservation(
                amount=Decimal("100"),
                contract_id=contract_id,
            ),
            first_settlement,
            duplicate_settlement,
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.realized_profit,
            Decimal("80"),
        )
        self.assertEqual(
            statistics.settled_stake,
            Decimal("100"),
        )
        self.assertIs(
            statistics.operations_by_contract[contract_id],
            first_settlement,
        )

    def test_should_return_zero_roi_without_settled_stake(self) -> None:
        """Deve retornar ROI zero sem capital liquidado."""

        statistics = BankrollStatistics()

        self.assertEqual(statistics.roi, ZERO)

    def test_should_calculate_positive_roi(self) -> None:
        """Deve calcular ROI positivo sobre a stake liquidada."""

        contract_id = uuid4()

        ledger = (
            self._create_stake_reservation(
                amount=Decimal("100"),
                contract_id=contract_id,
            ),
            self._create_win_settlement(
                amount=Decimal("180"),
                contract_id=contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.roi,
            Decimal("80"),
        )

    def test_should_calculate_negative_roi(self) -> None:
        """Deve calcular ROI negativo em uma operação LOSS."""

        contract_id = uuid4()

        ledger = (
            self._create_stake_reservation(
                amount=Decimal("100"),
                contract_id=contract_id,
            ),
            self._create_loss_settlement(
                contract_id=contract_id,
            ),
        )

        statistics = BankrollStatistics(ledger=ledger)

        self.assertEqual(
            statistics.roi,
            Decimal("-100"),
        )

    def test_should_return_zero_exposure_without_balance(self) -> None:
        """Deve retornar exposição zero quando a banca estiver zerada."""

        statistics = BankrollStatistics()

        self.assertEqual(statistics.exposure_rate, ZERO)

    def test_should_calculate_exposure_rate(self) -> None:
        """
        Exposição deve representar a parcela atualmente reservada.
        """

        statistics = BankrollStatistics(
            available_balance=Decimal("800"),
            reserved_balance=Decimal("200"),
        )

        self.assertEqual(
            statistics.exposure_rate,
            Decimal("20"),
        )

    def test_should_map_operations_by_contract(self) -> None:
        """Deve indexar liquidações pelo identificador do contrato."""

        win_contract_id = uuid4()
        loss_contract_id = uuid4()

        win_transaction = self._create_win_settlement(
            amount=Decimal("180"),
            contract_id=win_contract_id,
        )
        loss_transaction = self._create_loss_settlement(
            contract_id=loss_contract_id,
        )

        statistics = BankrollStatistics(
            ledger=(
                win_transaction,
                loss_transaction,
            ),
        )

        operations = statistics.operations_by_contract

        self.assertEqual(len(operations), 2)
        self.assertIs(
            operations[win_contract_id],
            win_transaction,
        )
        self.assertIs(
            operations[loss_contract_id],
            loss_transaction,
        )

    def test_operations_by_contract_should_be_read_only(self) -> None:
        """O mapeamento de operações não deve permitir alterações."""

        contract_id = uuid4()

        transaction = self._create_win_settlement(
            amount=Decimal("180"),
            contract_id=contract_id,
        )

        statistics = BankrollStatistics(
            ledger=(transaction,),
        )

        operations = statistics.operations_by_contract

        with self.assertRaises(TypeError):
            operations[uuid4()] = transaction  # type: ignore[index]

    def test_operations_by_contract_should_ignore_non_settlements(
        self,
    ) -> None:
        """O mapeamento deve ignorar transações não liquidadoras."""

        contract_id = uuid4()

        stake = self._create_stake_reservation(
            amount=Decimal("100"),
            contract_id=contract_id,
        )

        statistics = BankrollStatistics(ledger=(stake,))

        self.assertEqual(
            len(statistics.operations_by_contract),
            0,
        )

    @staticmethod
    def _create_generator(
        transactions: Iterable[BankrollTransaction],
    ) -> Iterable[BankrollTransaction]:
        """Cria um gerador de transações para os testes."""

        yield from transactions

    def _create_stake_reservation(
        self,
        amount: Decimal,
        contract_id: UUID,
    ) -> BankrollTransaction:
        """Cria uma transação de reserva de stake."""

        return self._create_transaction(
            transaction_type=BankrollTransactionType.STAKE_RESERVED,
            direction=BankrollTransactionDirection.DEBIT,
            amount=amount,
            contract_id=contract_id,
        )

    def _create_win_settlement(
        self,
        amount: Decimal,
        contract_id: UUID,
    ) -> BankrollTransaction:
        """Cria uma transação de liquidação WIN."""

        return self._create_transaction(
            transaction_type=BankrollTransactionType.SETTLEMENT_WIN,
            direction=BankrollTransactionDirection.CREDIT,
            amount=amount,
            contract_id=contract_id,
        )

    def _create_loss_settlement(
        self,
        contract_id: UUID,
    ) -> BankrollTransaction:
        """Cria uma transação neutra de liquidação LOSS."""

        return self._create_transaction(
            transaction_type=BankrollTransactionType.SETTLEMENT_LOSS,
            direction=BankrollTransactionDirection.NEUTRAL,
            amount=ZERO,
            contract_id=contract_id,
        )

    def _create_draw_settlement(
        self,
        amount: Decimal,
        contract_id: UUID,
    ) -> BankrollTransaction:
        """Cria uma transação de liquidação DRAW."""

        return self._create_transaction(
            transaction_type=BankrollTransactionType.SETTLEMENT_DRAW,
            direction=BankrollTransactionDirection.CREDIT,
            amount=amount,
            contract_id=contract_id,
        )

    def _create_transaction(
        self,
        transaction_type: BankrollTransactionType,
        direction: BankrollTransactionDirection,
        amount: Decimal,
        contract_id: UUID | None = None,
    ) -> BankrollTransaction:
        """Cria uma transação válida para os testes estatísticos."""

        return BankrollTransaction(
            transaction_id=uuid4(),
            transaction_type=transaction_type,
            direction=direction,
            amount=amount,
            created_at=datetime.now(timezone.utc),
            status=BankrollEntryStatus.REGISTERED,
            contract_id=contract_id,
            reference="TEST-REFERENCE",
            description="Bankroll statistics test transaction",
        )


if __name__ == "__main__":
    unittest.main()