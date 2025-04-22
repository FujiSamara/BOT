<script setup lang="ts">
import {
	onMounted,
	PropType,
	Ref,
	ref,
	useTemplateRef,
	markRaw,
	onUnmounted,
	watch,
} from "vue";
import {
	getDocument,
	GlobalWorkerOptions,
	PDFDocumentProxy,
	PDFPageProxy,
} from "pdfjs-dist";
import pdfjsWorker from "pdfjs-dist/build/pdf.worker?url";
GlobalWorkerOptions.workerSrc = pdfjsWorker;

import PulseSpinner from "@/components/UI-new/PulseSpinner.vue";
import { FileLinkSchema } from "@/components/knowledge/types";

const props = defineProps({
	file: {
		type: Object as PropType<FileLinkSchema>,
		required: true,
	},
	expanded: {
		type: Boolean,
	},
});

const canvaParent = useTemplateRef("parent");
const wrapper = useTemplateRef("wrapper");

const doc: Ref<PDFDocumentProxy | undefined> = ref(undefined);
const fullHeight: Ref<number> = ref(0);
const firstPageHeight: Ref<number> = ref(480);
const ready = ref(true);

const getCanvasID = (num: number) => {
	return `canvas-${num}`;
};

const renderDocument = async () => {
	if (!canvaParent.value) return;
	if (!doc.value) return;
	const wrapper = canvaParent.value;

	const createViewportContext = (page: PDFPageProxy) => {
		const canvas = document.getElementById(
			getCanvasID(page.pageNumber),
		) as HTMLCanvasElement;

		const actualWidth = page.view[2] - page.view[0] - 10;
		const scale = wrapper.offsetWidth / actualWidth;
		const viewport = page.getViewport({
			scale,
			offsetX: -5,
		});

		canvas.width = wrapper.offsetWidth;
		if (props.expanded) {
			canvas.height = viewport.height;
		} else {
			canvas.height =
				page.pageNumber === 1
					? Math.min(wrapper.offsetHeight, viewport.height)
					: 0;
		}

		const context = canvas.getContext("2d")!;
		const renderContext = {
			canvasContext: context,
			viewport: viewport,
		};

		return renderContext;
	};

	let height = 0;

	for (const num of Array(doc.value.numPages).keys()) {
		const pageId = num + 1;
		const page = await doc.value.getPage(pageId);
		const context = createViewportContext(page);

		if (pageId === 1) firstPageHeight.value = context.viewport.height;
		height += context.viewport.height;

		await page.render(context).promise;
	}

	fullHeight.value = height;
	normalizeParentHeight();
};
const normalizeParentHeight = async () => {
	if (!canvaParent.value) return;

	if (props.expanded) {
		canvaParent.value.style.height = `${fullHeight.value}px`;
	} else {
		const height = Math.min(480, firstPageHeight.value);
		canvaParent.value.style.height = `${height}px`;
	}
};

const loadFile = async () => {
	ready.value = false;
	doc.value = markRaw(await getDocument(props.file.url).promise);
	ready.value = true;
};

const expand = async () => {
	if (!canvaParent.value) return;

	await renderDocument();
	normalizeParentHeight();
};
watch(() => props.expanded, expand);

let resizeTimeout: number = setTimeout(() => {}, 0);
const onResize = async () => {
	if (!wrapper.value) return;

	clearTimeout(resizeTimeout);
	resizeTimeout = setTimeout(async () => {
		await renderDocument();
		normalizeParentHeight();
	}, 10);
};

let resizeObserver: ResizeObserver;
onMounted(async () => {
	if (!wrapper.value) return;

	await loadFile();
	if (!wrapper.value) return;
	resizeObserver = new ResizeObserver(onResize);
	if (!wrapper.value) return;
	resizeObserver.observe(wrapper.value);
});
onUnmounted(() => {
	if (!wrapper.value || !resizeObserver) return;

	resizeObserver.unobserve(wrapper.value);
	resizeObserver.disconnect();
});
</script>
<template>
	<div class="pdf-wrapper" ref="wrapper">
		<Transition name="fade" mode="out-in">
			<div v-if="ready && doc" class="canva-wrapper" ref="parent">
				<canvas v-for="num in doc.numPages" :id="getCanvasID(num)"></canvas>
			</div>
			<div v-else class="spinner-wrapper">
				<PulseSpinner class="spinner"></PulseSpinner>
			</div>
		</Transition>
	</div>
</template>
<style scoped lang="scss">
.pdf-wrapper {
	display: flex;
	width: 100%;

	.canva-wrapper {
		display: flex;
		flex-direction: column;
		align-items: center;

		width: 100%;
		height: 480px;

		border-radius: 16px;
	}

	.spinner-wrapper {
		display: flex;
		justify-content: center;
		align-items: center;

		width: 100%;
		height: 100%;

		.spinner {
			width: 128px;
			height: 128px;

			color: $main-accent-blue;
		}
	}
}
</style>
