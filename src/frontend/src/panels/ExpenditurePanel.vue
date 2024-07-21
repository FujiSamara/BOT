<template>
	<div class="expenditure-content">
		<div v-if="!editingElement" class="header-content">
			<h1>Заявки</h1>
			<PanelTools class="top-tools">
				<PeriodTool
					v-model:from-date="fromDateString"
					v-model:to-date="toDateString"
				></PeriodTool>
				<ToolSeparator></ToolSeparator>
				<SeacrhTool v-model:value="searchString"></SeacrhTool>
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
		<div v-if="editingElement" class="edit-panel-element-wrapper">
			<EditPanelElement
				class="edit-page"
				:inputHeaders="inputHeaders"
				:default-inputs="defaultInputs"
				@submit="onSubmit"
			></EditPanelElement>
		</div>
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
import { ExpenditureTable } from "@/table";

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

const table = new ExpenditureTable([], "expenditure");
const fromDateString = ref("");
const toDateString = ref("");
const searchString = ref("");

table.filters.value = computed((): Array<(instance: any) => boolean> => {
	const periodFilter = (instance: any): boolean => {
		const rowDate = new Date(instance.create_date);
		const fromDate = new Date(fromDateString.value);
		const toDate = new Date(toDateString.value);

		return rowDate <= toDate && rowDate >= fromDate;
	};
	return [periodFilter];
}).value;
table.searcher.value = computed((): ((instance: any) => boolean) => {
	return (instance: any): boolean => {
		const name: string = instance.name;
		if (name.indexOf(searchString.value) !== -1) {
			return true;
		}
		const chapter: string = instance.chapter;
		if (chapter.indexOf(searchString.value) !== -1) {
			return true;
		}
		return false;
	};
}).value;

const onRowClicked = (rowKey: number) => {
	defaultInputs.value = table.cloneRow(rowKey);
	defaultInputs.value.splice(0, 1);
	defaultInputs.value.splice(2, 1);
	editingElement.value = true;
};
const onCreateClicked = () => {
	defaultInputs.value = [];
	editingElement.value = true;
};
onMounted(async () => {
	await table.load();
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
.edit-panel-element-wrapper {
	height: 100%;
	display: flex;
	flex-direction: column;
	padding-top: 56px;
	padding-bottom: 56px;
}
</style>
