<template>
	<div class="expenditure-content">
		<div class="header-content">
			<h1>Заявки</h1>
			<PanelTools class="top-tools">
				<PeriodTool></PeriodTool>
				<ToolSeparator></ToolSeparator>
				<SeacrhTool></SeacrhTool>
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

import { ref } from "vue";
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
	"Дата создания",
	"Дата закрытия",
	"Работник",
	"Сумма",
	"Тип оплаты",
	"Производство",
	"Цель платежа",
	"Статус",
	"Комментарий",
];

const tableBody: Array<Array<string>> = [
	[
		"90",
		"2014.06.09",
		"2014.08.09",
		"9999",
		"Инфа на Сотку",
		"Безналичная",
		"Тольятти Автостроителей 56 Сайгина",
		"Оплата работ",
		"Согласовано КРУ",
		"Когда будет написано много текста, то он скорее всего будет просто пропадать и будут стоять точки, после 2-х строк",
	],
	[
		"91",
		"2014.06.09",
		"2014.08.09",
		"9999",
		"Инфа на Сотку",
		"Безналичная",
		"Тольятти Автостроителей 56 Сайгина",
		"Оплата работ",
		"Согласовано КРУ",
		"Когда будет написано много текста, то он скорее всего будет просто пропадать и будут стоять точки, после 2-х строк",
	],
	[
		"92",
		"2014.06.09",
		"2014.08.09",
		"9999",
		"Инфа на Сотку",
		"Безналичная",
		"Тольятти Автостроителей 56 Сайгина",
		"Оплата работ",
		"Согласовано КРУ",
		"Когда будет написано много текста, то он скорее всего будет просто пропадать и будут стоять точки, после 2-х строк",
	],
	[
		"93",
		"2014.06.09",
		"2014.08.09",
		"9999",
		"Инфа на Сотку",
		"Безналичная",
		"Тольятти Автостроителей 56 Сайгина",
		"Оплата работ",
		"Согласовано КРУ",
		"Когда будет написано много текста, то он скорее всего будет просто пропадать и будут стоять точки, после 2-х строк",
	],
	[
		"94",
		"2014.06.09",
		"2014.08.09",
		"9999",
		"Инфа на Сотку",
		"Безналичная",
		"Тольятти Автостроителей 56 Сайгина",
		"Оплата работ",
		"Согласовано КРУ",
		"Когда будет написано много текста, то он скорее всего будет просто пропадать и будут стоять точки, после 2-х строк",
	],
	[
		"95",
		"2014.06.09",
		"2014.08.09",
		"9999",
		"Инфа на Сотку",
		"Безналичная",
		"Тольятти Автостроителей 56 Сайгина",
		"Оплата работ",
		"Согласовано КРУ",
		"Когда будет написано много текста, то он скорее всего будет просто пропадать и будут стоять точки, после 2-х строк",
	],
];

const table = new Table(tableBody);

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
	width: 100%;
	height: 100%;
	display: flex;
	flex-direction: column;
	gap: 30px;
}
.header-content {
	width: 100%;
	padding-top: 20px;
	padding-right: 20px;
	display: flex;
	align-items: center;
	flex-direction: row;
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
