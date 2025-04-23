<script setup lang="ts">
import { onMounted, PropType, Ref, ref, useTemplateRef, watch } from "vue";

import * as XLSX from "xlsx";
import { Grid } from "gridjs";

import PulseSpinner from "@/components/UI-new/PulseSpinner.vue";
import { FileLinkSchema } from "@/components/knowledge/types";
import { useNetworkStore } from "@/store/network";

const props = defineProps({
	file: {
		type: Object as PropType<FileLinkSchema>,
		required: true,
	},
	expanded: {
		type: Boolean,
	},
});

const wrapper = useTemplateRef("wrapper");

const store = useNetworkStore();
const ready = ref(true);

const sheets: Ref<Array<{ name: string; headers: any; data: any }>> = ref([]);
const currentSheet = ref(0);

let grid: Grid | undefined;

const renderTable = async () => {
	if (!wrapper.value || sheets.value.length === 0) return;

	if (grid !== undefined) grid.destroy();

	grid = new Grid({
		columns: sheets.value[currentSheet.value].headers,
		data: sheets.value[currentSheet.value].data,
		sort: true,
		height: "100%",
		language: {
			search: {
				placeholder: "🔍 Поиск",
			},
			pagination: {
				previous: "Назад",
				next: "Вперед",
			},
		},
	});

	grid.render(wrapper.value);
};

const loadFile = async () => {
	ready.value = false;

	const data = await store.getFileByURL(props.file.url);
	const buffer = await data.arrayBuffer();

	const workbook = XLSX.read(buffer, { type: "array" });

	sheets.value = workbook.SheetNames.map((sheetName) => {
		const worksheet = workbook.Sheets[sheetName];
		const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

		const data: any[] = jsonData.slice(1);

		return {
			name: sheetName,
			headers: jsonData[0] as any,
			data: data.filter((row: any[]) =>
				row.some(
					(cell: any) => cell !== null && cell !== undefined && cell !== "",
				),
			) as any,
		};
	});

	ready.value = true;
};

watch([wrapper, sheets], renderTable);
watch(
	() => props.expanded,
	() => {
		if (!wrapper.value) return;

		const table = wrapper.value.getElementsByClassName(
			"gridjs-table",
		)[0]! as HTMLElement;

		if (props.expanded)
			wrapper.value.style.height = `${table.offsetHeight + 4}px`;
		else wrapper.value.style.height = "480px";
	},
);

onMounted(async () => {
	await loadFile();
});
</script>
<template>
	<Transition name="fade" mode="out-in">
		<div v-if="ready" class="excel-viewer">
			<div class="excel-wrapper" ref="wrapper"></div>
		</div>
		<div v-else class="spinner-wrapper">
			<PulseSpinner class="spinner"></PulseSpinner>
		</div>
	</Transition>
</template>
<style scoped lang="scss">
.excel-viewer {
	display: flex;
	flex-direction: column;
	width: 100%;

	.excel-wrapper {
		display: flex;
		flex-direction: column;
		align-items: center;

		width: 100%;
		height: 480px;

		border-radius: 16px;

		:deep(.gridjs-wrapper) {
			scrollbar-width: none;
		}
	}
}
</style>
