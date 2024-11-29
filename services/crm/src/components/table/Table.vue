<script setup lang="ts">
import { computed, onMounted, useTemplateRef } from "vue";
import TableCell from "@/components/table/TableCell.vue";
import { BaseSchema } from "@/types";
import { Table } from "@/components/table";

const props = defineProps({
	table: {
		type: Table<BaseSchema>,
		required: true,
	},
});

const tableRef = useTemplateRef("table");

const resizeTable = () => {
	const tableElement = tableRef.value as HTMLElement;
	const tableHeigth = tableElement.offsetHeight;

	const rowCount = Math.floor(tableHeigth / 64) - 1;

	props.table.rowsPerPage.value = rowCount;
};

const titles = computed(() => props.table.headers.value);

const rows = computed(() => props.table.rows.value);

onMounted(() => {
	resizeTable();
});
</script>

<template>
	<div class="p-table" ref="table">
		<TransitionGroup name="table" tag="div">
			<div class="t-row title" v-if="titles.length !== 0" :key="-1">
				<TableCell class="t-cell" v-for="title in titles" :key="title">{{
					title
				}}</TableCell>
			</div>
			<div class="t-row" v-for="row in rows" :key="row.id">
				<TableCell
					class="t-cell"
					v-for="(column, index) in row.columns"
					:key="index"
					>{{ column.cellLines[0].value }}</TableCell
				>
			</div>
		</TransitionGroup>
	</div>
</template>

<style scoped lang="scss">
.p-table {
	display: flex;
	flex-direction: column;

	flex-grow: 1;

	margin: 0;

	padding: 0 16px;
	border-radius: 16px;

	overflow-x: auto;

	background-color: $table-background-color;

	.t-row {
		display: flex;
		flex-direction: row;
		align-items: center;

		gap: 32px;
		height: 64px;
		min-height: 64px;
		max-height: 64px;
		width: fit-content;

		border-radius: 8px;

		padding: 0 24px;

		font-size: 14px;
		font-family: Wix Madefor Display;
		font-weight: 500;
		line-height: 17.64px;
		color: $text-color;

		&.title {
			font-size: 16px;
			line-height: 20.16px;
		}
	}

	.table-item {
		display: inline-block;
		margin-right: 10px;
	}
	.table-enter-active,
	.table-leave-active {
		transition: all 1s ease;
	}
	.table-enter-from,
	.table-leave-to {
		opacity: 0;
		transform: translateY(30px);
	}
}
</style>
