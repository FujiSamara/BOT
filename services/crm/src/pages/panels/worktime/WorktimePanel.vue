<script setup lang="ts">
import Table from "@/components/table/Table.vue";
import TablePagination from "@/components/table/TablePagination.vue";
import SearchInput from "@/components/table/tools/SearchInput.vue";
import ColumnFilter from "@/components/table/tools/ColumnFilter.vue";
import ExportToExcel from "@/components/table/tools/ExportToExcel.vue";
import DateFilter from "@/components/table/tools/DateFilter.vue";

import { Table as BaseTable } from "@/components/table";
import { BaseSchema } from "@/types";
import { useSearch } from "@/hooks/searchHook";
import { PropType } from "vue";
import { useDateInterval } from "@/hooks/dateIntervalHook";

const props = defineProps({
	table: {
		type: Object as PropType<BaseTable<BaseSchema>>,
		required: true,
	},
});

const searchList = useSearch(
	props.table,
	{
		schemas: [
			{
				pattern: "department",
				groups: [0],
			},
		],
		placeholder: "Производство",
		style: "height: 100%; width: 215px",
		name: "department",
	},
	{
		schemas: [
			{
				pattern: "worker",
				groups: [0],
			},
		],
		placeholder: "Поиск",
		style: "height: 100%; width: 170px",
		name: "general",
	},
);

const dateInterval = useDateInterval(props.table, "day");
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
						:value="search.value.value"
						@submit="search.onInput"
						:id="index"
					></SearchInput>
					<DateFilter
						@submit="dateInterval.submit"
						style="width: 245px; height: 48px"
					></DateFilter>
				</div>
			</div>
			<div class="tb-outer-group">
				<div class="tb-group">
					<ColumnFilter
						:style="'width: 126px; height: 48px'"
						:table="props.table"
					></ColumnFilter>
					<ExportToExcel
						:table="props.table"
						style="width: 187px; height: 48px"
					></ExportToExcel>
				</div>
			</div>
		</div>
		<Table class="table" :table="props.table"></Table>
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
