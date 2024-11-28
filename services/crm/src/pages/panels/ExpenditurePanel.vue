<script setup lang="ts">
import Table from "@/components/table/Table.vue";
import TablePagination from "@/components/table/TablePagination.vue";
import TableToolbar from "@/components/table/TableToolbar.vue";
</script>

<template>
	<div class="table-panel">
		<TableToolbar class="toolbar"></TableToolbar>
		<Table class="table"></Table>
		<TablePagination></TablePagination>
	</div>
</template>

<style scoped lang="scss">
.table-panel {
	@include tablePanel;
}
</style>
