<template>
	<div class="budget-content">
		<div class="header-content">
			<div class="top-tools">
				<h1>Заявки</h1>
			</div>
			<div class="fast-tools"></div>
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
.budget-content {
	width: 100%;
	height: 100%;
	display: flex;
	flex-direction: column;
	gap: 30px;
}
.header-content {
	width: 100%;
	height: 130px;
	border: 1px solid black;
}
.header-content h1 {
	font-family: Stolzl;
	font-size: 36px;
	font-weight: 600;
}
</style>
