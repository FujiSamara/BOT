<script setup lang="ts">
import { computed, PropType, ref } from "vue";
import { toast } from "vue3-toastify";

import PulseSpinner from "@/components/UI-new/PulseSpinner.vue";
import CardMaterials from "@/components/knowledge/CardMaterials.vue";
import PDFView from "@/components/viewer/PDFView.vue";
import ExcelViev from "@/components/viewer/ExcelViev.vue";

import { BusinessCard, getExt } from "@/components/knowledge/types";

const props = defineProps({
	card: {
		type: Object as PropType<BusinessCard>,
		required: true,
	},
	canEdit: {
		type: Boolean,
	},
});
const emits = defineEmits<{
	(e: "delete", materialId: number): void;
}>();

let warningComplete = false;

const expanded = ref(false);
const mainFile = computed(() => {
	if (props.card.materials === undefined) return;

	const file = props.card.materials.find((val) => {
		const ext = getExt(val);
		return ext === "xlsx" || ext === "pdf";
	});

	if (file === undefined) return;

	if (file.size / 1e6 > 3 && !warningComplete) {
		toast.warning(
			`Вес файла ${(file.size / 1e6).toFixed(2)} MB, возможна долгая загрузка.`,
			{
				autoClose: 10000,
			},
		);
		warningComplete = true;
	}

	return file;
});
const excelFile = computed(() => {
	if (mainFile.value === undefined) return;

	const file = mainFile.value;
	const ext = getExt(file);
	if (ext === "xlsx") return file;
});
const pdfFile = computed(() => {
	if (mainFile.value === undefined) return;

	const file = mainFile.value;
	const ext = getExt(file);
	if (ext === "pdf") return file;
});
</script>
<template>
	<div class="card-wrapper">
		<header>
			<h2 class="title">{{ props.card.name }}</h2>
			<span class="description">{{ props.card.description }}</span>
		</header>

		<Transition name="fade" mode="out-in">
			<footer
				v-if="props.card.materials !== undefined && props.card.materials.length"
				class="materials"
			>
				<div class="main-file">
					<PDFView
						v-if="pdfFile"
						:file="pdfFile"
						:expanded="expanded"
					></PDFView>
					<ExcelViev
						v-if="excelFile"
						:file="excelFile"
						:expanded="expanded"
					></ExcelViev>
					<div class="expand" @click="() => (expanded = !expanded)">
						<span>{{ expanded ? "Свернуть" : "Развернуть" }}</span>
						<span class="icon" :class="{ reversed: expanded }"></span>
					</div>
				</div>
				<CardMaterials
					:materials="props.card.materials"
					@delete="
						(index: number) => emits('delete', props.card.materials[index].id)
					"
					:can-delete="props.canEdit"
				></CardMaterials>
			</footer>
			<div
				v-else-if="props.card.materials === undefined"
				class="spinner-wrapper"
			>
				<PulseSpinner class="spinner"></PulseSpinner>
			</div>
		</Transition>
	</div>
</template>
<style scoped lang="scss">
@import url("./style.scss");
</style>
