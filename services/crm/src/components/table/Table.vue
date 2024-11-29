<script setup lang="ts">
import { computed } from "vue";
import TableCell from "@/components/table/TableCell.vue";
import { BaseSchema } from "@/types";
import { Table } from "@/components/table";

const props = defineProps({
	table: {
		type: Table<BaseSchema>,
	},
});

const titles = computed(() => {
	if (!props.table) return [];

	return props.table.headers.value;
});
</script>

<template>
	<div class="table">
		<div class="t-row">
			<TableCell class="t-cell" v-for="title in titles" :key="title">{{
				title
			}}</TableCell>
		</div>
		<div class="t-row"></div>
	</div>
</template>

<style scoped lang="scss">
.table {
	display: flex;
	flex-direction: column;
	justify-content: center;

	flex-grow: 1;

	margin: 0;

	padding: 0 16px;
	border-radius: 16px;

	background-color: $table-background-color;

	.t-row {
		display: flex;
		flex-direction: row;
	}
}
</style>
