<script setup lang="ts">
import Table from "@/components/table/Table.vue";
import TablePagination from "@/components/table/TablePagination.vue";
import SearchInput from "@/components/SearchInput.vue";
import ColumnFilter from "@/components/table/tools/ColumnFilter.vue";
import SearchFilter from "@/components/table/tools/SearchFilter.vue";
import ExportToExcel from "@/components/table/tools/ExportToExcel.vue";
import DateFilter from "@/components/table/tools/DateFilter.vue";
import CreateRow from "@/components/table/tools/CreateRow.vue";

import { Table as BaseTable } from "@/components/table";
import { BaseSchema } from "@/types";
import { PropType } from "vue";
import { setupWorktime } from "@/pages/panels/worktime";

const props = defineProps({
	table: {
		type: Object as PropType<BaseTable<BaseSchema>>,
		required: true,
	},
});

const setup = await setupWorktime(props.table);
</script>

<template>
	<div class="table-panel">
		<div class="toolbar">
			<div class="tb-outer-group">
				<div class="tb-group">
					<CreateRow></CreateRow>
					<SearchInput
						v-for="(search, index) in setup.searchList"
						:style="search.style"
						:placeholder="search.placeholder"
						:error="search.error.value"
						:value="search.value.value"
						@submit="search.onInput"
						:id="index"
					></SearchInput>
					<DateFilter
						:from="setup.dateInterval.from"
						:to="setup.dateInterval.to"
						@unset="setup.dateInterval.unset"
						@submit="setup.dateInterval.submit"
					></DateFilter>
				</div>
			</div>
			<div class="tb-outer-group">
				<div class="tb-group">
					<ColumnFilter
						:style="'height: 48px'"
						:table="props.table"
					></ColumnFilter>
					<SearchFilter
						:style="'height: 48px'"
						:entities="setup.entitySearchList.entities"
					></SearchFilter>
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
