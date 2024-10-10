<template>
	<div class="expenditure-content">
		<div v-show="!editingElement" class="header-content">
			<h1>Статьи</h1>
			<PanelTools class="top-tools">
				<PeriodTool
					v-model:from-date="fromDateString"
					v-model:to-date="toDateString"
				></PeriodTool>
				<ToolSeparator></ToolSeparator>
				<SeacrhTool
					id="topDepartmentSearch"
					placeholder="Производство"
					@input="(val) => (departmentSearchString = val)"
				></SeacrhTool>
				<SeacrhTool
					id="topSearch"
					@input="(val) => (searchString = val)"
				></SeacrhTool>
			</PanelTools>
		</div>
		<PanelTable
			v-show="!editingElement"
			:table="table"
			@click="onRowClicked"
			@create="onCreateClicked"
			:canCreate="true"
			:canDelete="true"
		></PanelTable>
		<div v-if="editingElement" class="edit-panel-element-wrapper">
			<EditPanelRow
				class="edit-page"
				:editor="editor"
				@submit="onSubmit"
				@close="editingElement = false"
			></EditPanelRow>
		</div>
	</div>
</template>
<script setup lang="ts">
import PanelTable from "@/components/PanelTable.vue";
import EditPanelRow from "@/components/EditPanelRow.vue";
import PanelTools from "@/components/PanelTools.vue";
import SeacrhTool from "@/components/PanelTools/SearchTool.vue";
import PeriodTool from "@/components/PanelTools/PeriodTool.vue";
import ToolSeparator from "@/components/PanelTools/ToolSeparator.vue";

import { onMounted, Ref, ref, shallowRef, ShallowRef, watch } from "vue";
import { ExpenditureTable } from "@/table";
import { ExpenditureEditor } from "@/editor";

const props = defineProps({
	id: {
		type: Number,
		required: true,
	},
});

const emit = defineEmits<{
	(e: "notify", count: number, id: number): void;
}>();

const editingElement = ref(false);

// Edit page
const editor: ShallowRef<ExpenditureEditor> = shallowRef(
	new ExpenditureEditor(),
);
const editingElementKey: Ref<number> = ref(-1);

const onSubmit = async () => {
	if (editingElementKey.value !== -1) {
		await table.update(editor.value.toInstanse(), editingElementKey.value);
	} else {
		await table.create(editor.value.toInstanse());
	}
	editingElement.value = false;
};

const table = new ExpenditureTable();
const fromDateString = ref("");
const toDateString = ref("");

const departmentSearchString = ref("");
const searchString = ref("");

watch([departmentSearchString, searchString], () => {
	const result = [];

	if (departmentSearchString.value.length > 3) {
		result.push({
			column: "creator",
			term: "",
			groups: [0, 1, 2],
			dependencies: [
				{
					column: "department",
					term: departmentSearchString.value,
				},
			],
		});
	}

	if (searchString.value.length > 3) {
		result.push(
			{
				column: "fac",
				term: searchString.value,
				groups: [0],
			},
			{
				column: "chapter",
				term: searchString.value,
				groups: [1],
			},
			{
				column: "name",
				term: searchString.value,
				groups: [2],
			},
		);
	}

	table.searchQuery.value = result;
});

watch([fromDateString, toDateString], () => {
	const fromDate = new Date(fromDateString.value);
	const toDate = new Date(toDateString.value);

	table.byDate.value = {
		column: "create_date",
		start: fromDate,
		end: toDate,
	};
});

const onRowClicked = (rowKey: number) => {
	editor.value = new ExpenditureEditor(table.getModel(rowKey));
	editingElementKey.value = rowKey;
	editingElement.value = true;
};
const onCreateClicked = () => {
	editor.value = new ExpenditureEditor();
	editingElementKey.value = -1;
	editingElement.value = true;
};
watch(table.notifies, () => {
	emit("notify", table.notifies.value, props.id);
});
onMounted(() => table.startUpdatingLoop());
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
	flex-shrink: 0;
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
