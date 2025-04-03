<script setup lang="ts">
import { onMounted, PropType, Ref, ref, useTemplateRef, markRaw } from "vue";
import {
	getDocument,
	GlobalWorkerOptions,
	PDFDocumentProxy,
	PDFPageProxy,
} from "pdfjs-dist";
import pdfjsWorker from "pdfjs-dist/build/pdf.worker?url";
GlobalWorkerOptions.workerSrc = pdfjsWorker;

import { FileLinkSchema } from "@/components/knowledge";

const props = defineProps({
	file: {
		type: Object as PropType<FileLinkSchema>,
		required: true,
	},
});

const canvaRef = useTemplateRef("canva");
const canvaParent = useTemplateRef("parent");

const doc: Ref<PDFDocumentProxy | undefined> = ref(undefined);
const currentPage: Ref<PDFPageProxy | undefined> = ref(undefined);
const height: Ref<number> = ref(0);

const renderPage = async () => {
	if (!canvaRef.value) return;
	if (!canvaParent.value) return;
	if (!currentPage.value) return;
	if (!doc.value) return;

	const canva = canvaRef.value;
	const wrapper = canvaParent.value;
	const page = currentPage.value;

	const resizeCanva = () => {
		canva.width = wrapper.offsetWidth;
		canva.height = wrapper.offsetHeight;
	};
	const createViewportContext = () => {
		const actualWidth = page.view[2] - page.view[0] - 10;
		const scale = wrapper.offsetWidth / actualWidth;
		const viewport = page.getViewport({ scale, offsetX: -5 });
		height.value = viewport.height;

		const context = canva.getContext("2d")!;
		const renderContext = {
			canvasContext: context,
			viewport: viewport,
		};

		return renderContext;
	};

	resizeCanva();
	const context = createViewportContext();
	await page.render(context);
};

defineExpose({ renderPage, actualHeight: height });

const loadFile = async () => {
	doc.value = markRaw(await getDocument(props.file.url).promise);
	currentPage.value = markRaw(await doc.value.getPage(1)); // TODO: Complete not only for first page.
};

onMounted(async () => {
	await loadFile();
	await renderPage();
});
</script>
<template>
	<div class="pdf-wrapper" ref="parent">
		<canvas id="pdf-canvas" ref="canva"></canvas>
	</div>
</template>
<style scoped lang="scss"></style>
