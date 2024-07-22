<template>
	<div class="table-wrapper">
		<table>
			<thead>
				<tr>
					<th>
						<div class="table-tools">
							<table-checkbox
								v-model:checked="mainCheckboxChecked"
								class="checkbox"
								id="main"
							></table-checkbox>
							<div class="table-actions">
								<clickable-icon
									v-show="mainCheckboxChecked || props.table.isAnyChecked()"
									v-if="canDelete"
									class="icons"
									img-src="/img/trash.svg"
									@click="onDelete"
								></clickable-icon>
								<clickable-icon
									v-if="canCreate"
									class="icons"
									img-src="/img/add-plus.svg"
									@click="emit('create')"
								></clickable-icon>
							</div>
						</div>
					</th>
					<th
						v-for="columnValue in props.table.headers.value"
						:key="columnValue"
					>
						{{ columnValue }}
					</th>
				</tr>
			</thead>
			<tbody>
				<tr
					v-for="row in table.data.value"
					:key="row.key"
					@click.prevent="$emit('click', row.key)"
					@mouseleave="table.isHighlighted(row.key).value = false"
					:class="{
						highlighted:
							table.isChecked(row.key).value ||
							table.isHighlighted(row.key).value,
					}"
				>
					<th>
						<div class="table-tools">
							<table-checkbox
								:id="row.key.toString()"
								v-model:checked="table.isChecked(row.key).value"
								class="checkbox"
							></table-checkbox>
						</div>
					</th>
					<th
						v-for="(columnValue, columnIndex) in row.columns"
						:key="columnIndex"
					>
						{{ columnValue }}
					</th>
				</tr>
				<tr>
					<th style="border: none"></th>
				</tr>
			</tbody>
		</table>
		<div v-if="table.isLoading.value" class="loader-space">
			<circle-loader></circle-loader>
		</div>
	</div>
</template>
<script setup lang="ts">
import { ref, watch } from "vue";
import ClickableIcon from "./UI/ClickableIcon.vue";
import type { Table } from "@/table";
import type { PropType } from "vue";

const props = defineProps({
	table: {
		type: Object as PropType<Table>,
		required: true,
	},
	canCreate: {
		type: Boolean,
		required: false,
	},
	canDelete: {
		type: Boolean,
		required: false,
	},
});

const emit = defineEmits(["click", "create", "delete"]);

const mainCheckboxChecked = ref(false);

watch(mainCheckboxChecked, () => {
	for (let index = 0; index < props.table.data.value.length; index++) {
		props.table.isChecked(props.table.data.value[index].key).value =
			mainCheckboxChecked.value;
	}
});

const onDelete = () => {
	props.table.deleteChecked();
	emit("delete");
};
</script>
<style scoped>
.table-wrapper {
	background-color: #ffffff;
	overflow-y: auto;
	overflow-x: auto;
	white-space: nowrap;
	overscroll-behavior: none;
	height: fit-content;

	border-radius: 20px;
	border: 1px solid #e6e6e6;
	max-width: 100%;
	width: min-content;
}

.table-wrapper::-webkit-scrollbar {
	width: 5px;
	height: 5px;
	border-radius: 2000px;
}

.table-wrapper::-webkit-scrollbar-track {
	background-color: #e7e7e7;
	margin: 20px;
}

.table-wrapper::-webkit-scrollbar-thumb:vertical,
.table-wrapper::-webkit-scrollbar-thumb:horizontal {
	height: 10px;
	width: 5px;
	height: 15px !important;
	border-radius: 22px;
	background-color: #993ca6;
}

table {
	height: fit-content;

	/** border */
	border-collapse: collapse;
	border-spacing: 0;
}

/** Cell border  */
tbody tr th {
	border-bottom: 1px solid #e6e6e6;
	border-right: 1px solid #e6e6e6;
}
tbody tr:first-child th {
	border-top: 1px solid #e6e6e6;
}

/** Empty up and down border */
tbody tr th:last-child {
	border-right: none;
}
tbody tr:last-child th {
	border-bottom: none;
}

/** Bottom row */
tbody tr:last-child th {
	padding: 10px;
}

/** Row selection */
tr:not(:last-child):hover {
	background-color: #fdf7fd;
}

/** Table head settings  */
thead tr th:first-child {
	border-top-left-radius: 20px;
}

thead tr th:last-child {
	border-top-right-radius: 20px;
}

thead {
	position: sticky;
	top: 0;
	left: 0;
	z-index: 1;
}

thead th {
	border: none;
	font-weight: 600;
	padding-bottom: 20px;
	padding-top: 30px;

	color: black;
	background-color: #ffffff;
}

/** All cells */
th {
	padding: 20px;
	color: #7f7f7f;
	font-family: Stolzl;
	font-size: 15px;
	font-weight: 400;
	min-width: 60px;
	text-align: center;
	position: relative;
}

.highlighted {
	background-color: #fdf7fd;
}

.table-tools {
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: flex-start;
	gap: 20px;
}

.table-actions {
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: center;
	gap: 10px;
}

.icons {
	width: 20px;
}

.loader-space {
	display: flex;
	width: 100%;
	min-height: 70px;
	position: relative;
	justify-content: center;
}
</style>
