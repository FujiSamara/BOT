import { BidTable } from "@/table";
import { Ref, watch } from "vue";

export const useBidSearchingHook = (
	departmentSearchString: Ref<string>,
	searchString: Ref<string>,
	table: BidTable,
) => {
	watch([departmentSearchString, searchString], () => {
		const result = [];

		if (departmentSearchString.value.length > 3) {
			result.push({
				column: "department",
				term: departmentSearchString.value,
				groups: [0, 1, 2, 3],
			});
		}

		if (searchString.value.length > 0) {
			result.push(
				{
					column: "worker",
					term: searchString.value,
					groups: [0],
				},
				{
					column: "expenditure",
					term: searchString.value,
					groups: [1],
				},
				{
					column: "id",
					term: searchString.value,
					groups: [2],
				},
				{
					column: "amount",
					term: searchString.value,
					groups: [3],
				},
			);
		}

		table.searchQuery.value = result;
	});
};
