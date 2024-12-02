<script setup lang="ts">
import Table from "@/components/table/Table.vue";
import TablePagination from "@/components/table/TablePagination.vue";

import { Table as BaseTable } from "@/components/table";
import { BaseSchema } from "@/types";
import SearchInput from "@/components/table/tools/SearchInput.vue";

const props = defineProps({
	table: {
		type: BaseTable<BaseSchema>,
		required: true,
	},
});
</script>

<template>
	<div class="table-panel">
		<div class="toolbar">
			<div class="tb-outer-group">
				<div class="tb-group">
					<SearchInput
						style="height: 100%; width: 215px"
						placeholder="Производство"
						:error="'Тестовая ошибка'"
					></SearchInput>
					<SearchInput
						style="height: 100%; width: 170px"
						placeholder="Поиск"
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
