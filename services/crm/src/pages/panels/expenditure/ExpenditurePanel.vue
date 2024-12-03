<script setup lang="ts">
import Table from "@/components/table/Table.vue";
import TablePagination from "@/components/table/TablePagination.vue";
import SearchInput from "@/components/table/tools/SearchInput.vue";
import ColumnFilter from "@/components/table/tools/ColumnFilter.vue";

import { Table as BaseTable } from "@/components/table";
import { BaseSchema } from "@/types";
import { useSearch } from "@/hooks/searchHook";
import ExportToExcel from "@/components/table/tools/ExportToExcel.vue";

const props = defineProps({
	table: {
		type: BaseTable<BaseSchema>,
		required: true,
	},
});

const searchList = useSearch(
	props.table,
	{
		schemas: [
			{
				pattern: "creator.department",
				groups: [0, 1, 2],
			},
		],
		placeholder: "Производство",
		style: "height: 100%; width: 215px",
	},
	{
		schemas: [
			{
				pattern: "fac",
				groups: [0],
			},
			{
				pattern: "chapter",
				groups: [1],
			},
			{
				pattern: "name",
				groups: [2],
			},
		],
		placeholder: "Поиск",
		style: "height: 100%; width: 170px",
	},
);
</script>

<template>
	<div class="table-panel">
		<div class="toolbar">
			<div class="tb-outer-group">
				<div class="tb-group">
					<SearchInput
						v-for="(search, index) in searchList"
						:style="search.style"
						:placeholder="search.placeholder"
						:error="search.error.value"
						@submit="search.onInput"
						:id="index"
					></SearchInput>
				</div>
			</div>
			<div class="tb-outer-group">
				<div class="tb-group">
					<ColumnFilter style="width: 126px; height: 48px"></ColumnFilter>
					<ExportToExcel style="width: 187px; height: 48px"></ExportToExcel>
				</div>
			</div>
		</div>
		<Table class="p-table" :table="props.table"></Table>
		<TablePagination
			v-model:currentPage="props.table.currentPage.value"
			:pageCount="props.table.pageCount.value"
		></TablePagination>
	</div>
</template>

<style scoped lang="scss">
.table-panel {
	@include tablePanel;
}
</style>
