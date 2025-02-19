import { FilterSchema } from "@/types";
import { EnumRecord } from "@/components/entity";

export enum BidState {
	Fac = "fac",
	CC = "cc",
	Paralegal = "paralegal",
	KRU = "kru",
	FinancialDirectorPending = "findir-pending",
	TellerPending = "teller-pending",
	TellerApproved = "teller-approved",
	Denied = "denied",
}

export function filterBidByStatus(selected: EnumRecord): FilterSchema[] {
	let result: FilterSchema[] = [];

	switch (selected.value) {
		case BidState.Fac:
			result = [
				{
					column: "fac_state",
					value: "pending_approval",
				},
			];
			break;

		case BidState.CC:
			result = [
				{
					column: "cc_state",
					value: "pending_approval",
				},
			];
			break;

		case BidState.Paralegal:
			result = [
				{
					column: "paralegal_state",
					value: "pending_approval",
				},
			];
			break;

		case BidState.KRU:
			result = [
				{
					column: "kru_state",
					value: "pending_approval",
				},
			];
			break;

		case BidState.FinancialDirectorPending:
			result = [
				{
					column: "accountant_cash_state",
					value: "pending_approval",
				},
				{
					column: "accountant_card_state",
					value: "pending_approval",
				},
			];
			break;

		case BidState.TellerPending:
			result = [
				{
					column: "teller_cash_state",
					value: "pending_approval",
				},
				{
					column: "teller_card_state",
					value: "pending_approval",
				},
			];
			break;

		case BidState.TellerApproved:
			result = [
				{
					column: "teller_cash_state",
					value: "approved",
				},
				{
					column: "teller_card_state",
					value: "approved",
				},
			];
			break;
		case BidState.Denied:
			result = [
				{
					column: "fac_state",
					value: "denied",
				},
				{
					column: "cc_state",
					value: "denied",
				},
				{
					column: "paralegal_state",
					value: "denied",
				},
				{
					column: "kru_state",
					value: "denied",
				},
				{
					column: "accountant_cash_state",
					value: "denied",
				},
				{
					column: "accountant_card_state",
					value: "denied",
				},
				{
					column: "teller_cash_state",
					value: "denied",
				},
				{
					column: "teller_card_state",
					value: "denied",
				},
			];
			break;
	}

	return result;
}
