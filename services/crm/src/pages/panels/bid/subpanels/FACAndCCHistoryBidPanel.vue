<script setup lang="ts">
import Table from "@/components/table/Table.vue";
import TablePagination from "@/components/table/TablePagination.vue";
import SearchInput from "@/components/MaybeDelayInput.vue";
import ColumnFilter from "@/components/table/tools/ColumnFilter.vue";
import SearchFilter from "@/components/table/tools/SearchFilter.vue";
import ExportToExcel from "@/components/table/tools/ExportToExcel.vue";
import DateFilter from "@/components/table/tools/DateFilter.vue";
import RowEditor from "@/components/table/RowEditor.vue";
import CoordinationControl from "@/pages/panels/bid/CoordinationControl.vue";

import { PropType } from "vue";
import { FACAndCCBidHistoryTable, setupBid } from "@/pages/panels/bid";
import { useRoute, useRouter } from "vue-router";

const props = defineProps({
	table: {
		type: Object as PropType<FACAndCCBidHistoryTable>,
		required: true,
	},
});

const route = useRoute();
const router = useRouter();
const setup = await setupBid(props.table, { router, route });
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
		<Table
			class="table"
			:table="props.table"
			@rowClick="setup.rowEditor.view"
		></Table>
		<TablePagination
			v-model:currentPage="props.table.currentPage.value"
			:pageCount="props.table.pageCount.value"
		></TablePagination>

		<RowEditor :editor="setup.rowEditor">
			<template #view>
				<CoordinationControl :editor="setup.rowEditor"></CoordinationControl>
			</template>
		</RowEditor>
	</div>
</template>

<style scoped lang="scss">
.table-panel {
	@include tablePanel;
}
</style>
