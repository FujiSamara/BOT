<script setup lang="ts">
import { computed, PropType } from "vue";
import { useRoute, useRouter } from "vue-router";

import Table from "@/components/table/Table.vue";
import TablePagination from "@/components/table/TablePagination.vue";
import SearchInput from "@/components/MaybeDelayInput.vue";
import ColumnFilter from "@/components/table/tools/ColumnFilter.vue";
import SearchFilter from "@/components/table/tools/SearchFilter.vue";
import ExportToExcel from "@/components/table/tools/ExportToExcel.vue";
import DateFilter from "@/components/table/tools/DateFilter.vue";

import { setupTimesheet, TimesheetTable } from "@/pages/panels/timesheet";

const props = defineProps({
	table: {
		type: Object as PropType<TimesheetTable>,
		required: true,
	},
});

const route = useRoute();
const router = useRouter();
const setup = await setupTimesheet(props.table, { router, route });

const filtersExist = computed(
	() => setup.dateInterval.exist.value && setup.entitySearchList.exist.value,
);
</script>

<template>
	<div class="table-panel">
		<div class="toolbar">
			<div class="tb-outer-group">
				<div class="tb-group">
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
						:block-unset="!props.table.blockLoop.value"
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
						:disabled="!filtersExist"
					></ExportToExcel>
				</div>
			</div>
		</div>
		<Table
			class="table"
			:table="props.table"
			:blockLoading="!filtersExist"
		></Table>
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
