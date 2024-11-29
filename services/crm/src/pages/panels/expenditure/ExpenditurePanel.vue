<script setup lang="ts">
import Table from "@/components/table/Table.vue";
import TablePagination from "@/components/table/TablePagination.vue";
import TableToolbar from "@/components/table/TableToolbar.vue";

import { Table as BaseTable } from "@/components/table";
import { BaseSchema } from "@/types";

const props = defineProps({
	table: {
		type: BaseTable<BaseSchema>,
		required: true,
	},
});
</script>

<template>
	<div class="table-panel">
		<TableToolbar class="toolbar"></TableToolbar>
		<Table class="p-table" :table="props.table"></Table>
		<TablePagination></TablePagination>
	</div>
</template>

<style scoped lang="scss">
.table-panel {
	@include tablePanel;
}
</style>
