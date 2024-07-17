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

import { computed, ref } from "vue";
import { Table } from "@/types";

const editingElement = ref(false);

// Edit page
const inputHeaders: Array<string> = [
	"Расстояние завершения заказа",
	"Время сгорания заказа",
	"Количество заказов в одни руки",
];

const defaultInputs: Array<string> = ["100 м.", "", "123"];

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

const tableBody: Array<Array<string>> = [
	[
		"1",
		"Контрольные закупки ОКК",
		"Контрольные закупки",
		"2014.06.09",
		"Саркисян А.",
		"Марданов И.",
		"Сайгина О.",
		"100000",
	],
	[
		"2",
		"Контрольные закупки ОКК",
		"Контрольные закупки",
		"2015.06.09",
		"Саркисян А.",
		"Марданов И.",
		"Сайгина О.",
		"100000",
	],
	[
		"3",
		"Контрольные закупки ОКК",
		"Контрольные закупки",
		"2016.06.09",
		"Саркисян А.",
		"Марданов И.",
		"Сайгина О.",
		"100000",
	],
	[
		"4",
		"Контрольные закупки ОКК",
		"Контрольные закупки",
		"2013.06.09",
		"Саркисян А.",
		"Марданов И.",
		"Сайгина О.",
		"100000",
	],
	[
		"5",
		"Контрольные закупки ОКК",
		"Контрольные закупки",
		"2012.06.09",
		"Саркисян А.",
		"Марданов И.",
		"Сайгина О.",
		"100000",
	],
];

const table = new Table(tableBody, [0, 4]);

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

const onRowClicked = (rowIndex: number) => {
	console.log(rowIndex);
	editingElement.value = true;
};
const onCreateClicked = () => {
	editingElement.value = true;
};
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
