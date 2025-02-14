<script setup lang="ts">
import { PropType } from "vue";
import { useRoute, useRouter } from "vue-router";

import Table from "@/components/table/Table.vue";
import TablePagination from "@/components/table/TablePagination.vue";
import SearchInput from "@/components/MaybeDelayInput.vue";
import ColumnFilter from "@/components/table/tools/ColumnFilter.vue";
// import DateFilter from "@/components/table/tools/DateFilter.vue";

import { ExpenditureTable, setupExpenditre } from "@/pages/panels/expenditure";

const props = defineProps({
	table: {
		type: Object as PropType<ExpenditureTable>,
		required: true,
	},
});

const route = useRoute();
const router = useRouter();
const setup = await setupExpenditre(props.table, { router, route });
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
					<!-- <DateFilter style="width: 245px; height: 48px"></DateFilter> -->
				</div>
			</div>
			<div class="tb-outer-group">
				<div class="tb-group">
					<ColumnFilter
						:style="'height: 48px'"
						:table="props.table"
						:alignRight="true"
					></ColumnFilter>
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
