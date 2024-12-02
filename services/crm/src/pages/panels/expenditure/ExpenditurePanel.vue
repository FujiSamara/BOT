<script setup lang="ts">
import Table from "@/components/table/Table.vue";
import TablePagination from "@/components/table/TablePagination.vue";
import SearchInput from "@/components/table/tools/SearchInput.vue";

import { Table as BaseTable } from "@/components/table";
import { BaseSchema } from "@/types";
import { useSearch } from "@/hooks/searchHook";

const props = defineProps({
	table: {
		type: BaseTable<BaseSchema>,
		required: true,
	},
});

const listeners = useSearch(
	props.table,
	{
		schemas: [
			{
				pattern: "creator.department",
				groups: [0, 1, 2],
			},
		],
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
	},
);
</script>

<template>
	<div class="table-panel">
		<div class="toolbar">
			<div class="tb-outer-group">
				<div class="tb-group">
					<SearchInput
						style="height: 100%; width: 215px"
						placeholder="Производство"
						@submit="listeners[0].onInput"
					></SearchInput>
					<SearchInput
						style="height: 100%; width: 170px"
						placeholder="Поиск"
						@submit="listeners[1].onInput"
					></SearchInput>
				</div>
			</div>
			<div class="tb-outer-group"></div>
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
