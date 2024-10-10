<template>
	<div class="worktime-content">
		<div v-if="!editingElement" class="header-content">
			<h1>Явки</h1>
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
				<ToolSeparator></ToolSeparator>
				<ExportTool :callback="table.export.bind(table)"></ExportTool>
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
import ExportTool from "@/components/PanelTools/ExportTool.vue";
import ToolSeparator from "@/components/PanelTools/ToolSeparator.vue";
import PeriodTool from "@/components/PanelTools/PeriodTool.vue";

import { onMounted, Ref, ref, shallowRef, ShallowRef, watch } from "vue";
import { WorkTimeTable } from "@/table";
import { WorkTimeEditor } from "@/editor";

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
const editor: ShallowRef<WorkTimeEditor> = shallowRef(new WorkTimeEditor());
const editingElementKey: Ref<number> = ref(-1);

const onSubmit = async () => {
	if (editingElementKey.value !== -1) {
		await table.update(editor.value.toInstanse(), editingElementKey.value);
	} else {
		await table.create(editor.value.toInstanse());
	}
	editingElement.value = false;
};

const table = new WorkTimeTable();
const fromDateString = ref("");
const toDateString = ref("");

const departmentSearchString = ref("");
const searchString = ref("");

watch([departmentSearchString, searchString], () => {
	const result = [];

	if (departmentSearchString.value.length > 3) {
		result.push({
			column: "department",
			term: departmentSearchString.value,
			groups: [0],
		});
	}

	if (searchString.value.length > 3) {
		result.push({
			column: "worker",
			term: searchString.value,
			groups: [0],
		});
	}

	table.searchQuery.value = result;
});

watch([fromDateString, toDateString], () => {
	const fromDate = new Date(fromDateString.value);
	const toDate = new Date(toDateString.value);

	table.byDate.value = {
		column: "day",
		start: fromDate,
		end: toDate,
	};
});

const onRowClicked = (rowKey: number) => {
	editor.value = new WorkTimeEditor(table.getModel(rowKey));
	editingElementKey.value = rowKey;
	editingElement.value = true;
};
const onCreateClicked = () => {
	editor.value = new WorkTimeEditor();
	editingElementKey.value = -1;
	editingElement.value = true;
};
watch(table.notifies, () => {
	emit("notify", table.notifies.value, props.id);
});
onMounted(() => table.startUpdatingLoop());
</script>
<style scoped>
.worktime-content {
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
