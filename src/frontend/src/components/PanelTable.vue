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
									v-show="mainCheckboxChecked"
									v-if="canDelete"
									class="icons"
									img-src="/img/trash.svg"
								></clickable-icon>
								<clickable-icon
									v-if="canCreate"
									class="icons"
									img-src="/img/add-plus.svg"
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
					v-for="(row, rowIndex) in tableBody"
					:key="row.id"
					@click.prevent="$emit('click', row.id)"
					@mouseleave="rowsHighlighted[rowIndex].highlighted = false"
					:class="{
						highlighted:
							rowsChecked[rowIndex].checked ||
							rowsHighlighted[rowIndex].highlighted,
					}"
				>
					<th>
						<div class="table-tools">
							<table-checkbox
								:checked="rowsChecked[rowIndex].checked"
								@update:checked="
									(value: boolean) => (rowsChecked[rowIndex].checked = value)
								"
								class="checkbox"
							></table-checkbox>
							<div class="table-actions">
								<clickable-icon
									v-show="!mainCheckboxChecked && rowsChecked[rowIndex].checked"
									v-if="canDelete"
									class="icons"
									img-src="/img/trash.svg"
								></clickable-icon>
							</div>
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
import { onMounted, onUnmounted, Ref, ref, watch } from "vue";
import ClickableIcon from "./UI/ClickableIcon.vue";

const props = defineProps({
	tableHead: {
		type: Array<String>,
		required: true,
	},
	tableBody: {
		type: Array<{ id: number; columns: Array<String> }>,
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

const emit = defineEmits(["click", "checked", "highlighted"]);

const tableWrapper: any = ref(null);

const rowsChecked: Ref<Array<{ checked: boolean; id: number }>> = ref([]);
const rowsHighlighted: Ref<Array<{ highlighted: boolean; id: number }>> = ref(
	[],
);
const updateRowsChecked = () => {
	const newRowsChecked: Array<{ checked: boolean; id: number }> = [];

	for (let index = 0; index < props.tableBody.length; index++) {
		const row = props.tableBody[index];

		newRowsChecked.push({ checked: false, id: row.id });

		for (const value of rowsChecked.value) {
			if (value.id === row.id) {
				newRowsChecked[index].checked = value.checked;
				break;
			}
		}
	}

	rowsChecked.value = newRowsChecked;
};
const updateRowsHighlighted = () => {
	const newRowsHighlighted: Array<{ highlighted: boolean; id: number }> = [];

	for (let index = 0; index < props.tableBody.length; index++) {
		const row = props.tableBody[index];

		newRowsHighlighted.push({ highlighted: false, id: row.id });

		for (const value of rowsHighlighted.value) {
			if (value.id === row.id) {
				newRowsHighlighted[index].highlighted = value.highlighted;
				break;
			}
		}
	}

	rowsHighlighted.value = newRowsHighlighted;
};
updateRowsChecked();
updateRowsHighlighted();

// Setted table width by all parent container width
const resizeTable = () => {
	tableWrapper.value.style.width = 0;
	tableWrapper.value.style.width =
		tableWrapper.value.parentElement.getBoundingClientRect().width + "px";
};
const mainCheckboxChecked = ref(false);

watch(mainCheckboxChecked, () => {
	for (let index = 0; index < rowsChecked.value.length; index++) {
		rowsChecked.value[index].checked = mainCheckboxChecked.value;
	}
});
watch(props.tableBody, () => {
	updateRowsChecked();
	updateRowsHighlighted();
});
watch(rowsChecked, () => emit("checked", rowsChecked.value), { deep: true });
watch(rowsHighlighted, () => emit("checked", rowsHighlighted.value), {
	deep: true,
});

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
