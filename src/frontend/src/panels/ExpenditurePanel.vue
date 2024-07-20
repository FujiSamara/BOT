<template>
	<div class="expenditure-content">
		<div class="header-content">
			<h1>Заявки</h1>
			<PanelTools class="top-tools">
				<PeriodTool
					v-model:from-date="fromDateString"
					v-model:to-date="toDateString"
				></PeriodTool>
				<ToolSeparator></ToolSeparator>
				<SeacrhTool v-model:value="table.searchString.value"></SeacrhTool>
				<ToolSeparator></ToolSeparator>
				<ExportTool></ExportTool>
			</PanelTools>
		</div>
		<PanelTable
			v-if="!editingElement"
			:table="table"
			:tableHead="tableHead"
			@click="onRowClicked"
			@create="onCreateClicked"
			:canCreate="true"
			:canDelete="true"
		></PanelTable>
		<EditPanelElement
			v-if="editingElement"
			:inputHeaders="inputHeaders"
			:default-inputs="defaultInputs"
			@submit="onSubmit"
		></EditPanelElement>
	</div>
</template>
<script setup lang="ts">
import PanelTable from "@/components/PanelTable.vue";
import EditPanelElement from "@/components/EditPanelElement.vue";
import PanelTools from "@/components/PanelTools.vue";
import SeacrhTool from "@/components/PanelTools/SearchTool.vue";
import ExportTool from "@/components/PanelTools/ExportTool.vue";
import PeriodTool from "@/components/PanelTools/PeriodTool.vue";
import ToolSeparator from "@/components/PanelTools/ToolSeparator.vue";

import { computed, onMounted, Ref, ref } from "vue";
import { Table } from "@/types";
import usePanelDataHandler from "@/hooks/panel";

const editingElement = ref(false);

// Edit page
const inputHeaders: Array<string> = [
	"Статья",
	"Раздел",
	"ЦФО",
	"ЦЗ",
	"Руководитель ЦЗ",
	"Лимит",
];

const defaultInputs: Ref<Array<string>> = ref([]);

const onSubmit = (inputs: Array<string>) => {
	editingElement.value = false;
	console.log(inputs);
};

// Table
const tableHead = [
	"ID",
	"Статья",
	"Раздел",
	"Дата создания",
	"ЦФО",
	"ЦЗ",
	"Руководитель ЦЗ",
	"Лимит",
];

const table = new Table([], [0, 4]);

const panelDataHandler = usePanelDataHandler(table, "expenditure");
if (!panelDataHandler) {
	throw Error("Panel not exist");
}

const fromDateString = ref("");
const toDateString = ref("");

table.filters.value = computed(
	(): Array<(row: { id: number; columns: Array<string> }) => boolean> => {
		const periodFilter = (row: {
			id: number;
			columns: Array<string>;
		}): boolean => {
			const rowDate = new Date(row.columns[3]);
			const fromDate = new Date(fromDateString.value);
			const toDate = new Date(toDateString.value);

			return rowDate <= toDate && rowDate >= fromDate;
		};
		return [periodFilter];
	},
).value;

const onRowClicked = (rowID: number) => {
	defaultInputs.value = table.cloneRow(rowID);
	defaultInputs.value.splice(0, 1);
	defaultInputs.value.splice(2, 1);
	editingElement.value = true;
};
const onCreateClicked = () => {
	editingElement.value = true;
};
onMounted(async () => {
	await panelDataHandler.loadData();
});
</script>
<style scoped>
.expenditure-content {
	height: 100%;
	display: flex;
	flex-direction: column;
	gap: 30px;
}
.header-content {
	padding-top: 20px;
	padding-right: 20px;
	display: flex;
	align-items: center;
	flex-direction: row;
	overflow: hidden;
}
.header-content h1 {
	font-family: Stolzl;
	font-size: 36px;
	font-weight: 550;
	margin: 0;
}
.top-tools {
	margin-left: auto;
}
</style>
