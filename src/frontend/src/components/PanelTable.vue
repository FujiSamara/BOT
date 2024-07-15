<template>
	<div class="table-wrapper" ref="tableWrapper">
		<table>
			<thead>
				<tr>
					<th>
						<div class="table-tools">
							<table-checkbox
								v-model:checked="mainCheckboxChecked"
								class="checkbox"
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
						v-for="(columnValue, rowIndex) in props.tableHead"
						:key="rowIndex"
					>
						{{ columnValue }}
					</th>
				</tr>
			</thead>
			<tbody>
				<tr
					v-for="row in table.data.value"
					:key="row.id"
					@click.prevent="$emit('click', row.id)"
					@mouseleave="table.isHighlighted(row.id).value = false"
					:class="{
						highlighted:
							table.isChecked(row.id).value ||
							table.isHighlighted(row.id).value,
					}"
				>
					<th>
						<div class="table-tools">
							<table-checkbox
								v-model:checked="table.isChecked(row.id).value"
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
					<th></th>
				</tr>
			</tbody>
		</table>
	</div>
</template>
<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from "vue";
import ClickableIcon from "./UI/ClickableIcon.vue";
import { Table } from "@/types";

const props = defineProps({
	tableHead: {
		type: Array<String>,
		required: true,
	},
	table: {
		type: Table,
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

const tableWrapper: any = ref(null);

const mainCheckboxChecked = ref(false);

// Setted table width by all parent container width
const resizeTable = () => {
	tableWrapper.value.style.width = 0;
	tableWrapper.value.style.width =
		tableWrapper.value.parentElement.getBoundingClientRect().width + "px";
};

watch(mainCheckboxChecked, () => {
	for (let index = 0; index < props.table.data.value.length; index++) {
		props.table.isChecked(props.table.data.value[index].id).value =
			mainCheckboxChecked.value;
	}
});

const onDelete = () => {
	props.table.deleteChecked();
	emit("delete");
};

onMounted(() => {
	window.addEventListener("resize", resizeTable);
	resizeTable();
});
onUnmounted(() => {
	window.removeEventListener("resize", resizeTable);
});
</script>
<style scoped>
.table-wrapper {
	overflow-y: scroll;
	overflow-x: scroll;
	white-space: nowrap;
	overscroll-behavior: none;
	height: fit-content;

	border-radius: 20px;
	border: 1px solid #e6e6e6;
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

	background-color: #ffffff;

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
</style>
