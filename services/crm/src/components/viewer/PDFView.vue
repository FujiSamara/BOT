<script setup lang="ts">
import {
	onMounted,
	PropType,
	useTemplateRef,
	onUnmounted,
	nextTick,
	computed,
} from "vue";

import PulseSpinner from "@/components/UI-new/PulseSpinner.vue";
import { FileLinkSchema } from "@/components/knowledge/types";
import { usePdfViewer } from "@/components/viewer/pdfviewer";

const props = defineProps({
	file: {
		type: Object as PropType<FileLinkSchema>,
		required: true,
	},
	expanded: {
		type: Boolean,
	},
});

const expanded = computed(() => props.expanded);

const container = useTemplateRef("container");
const wrapper = useTemplateRef("wrapper");
const viewer = usePdfViewer(container, wrapper, expanded);

let resizeObserver: ResizeObserver;
onMounted(async () => {
	await viewer.loadFile(props.file.url);
	await nextTick();
	await viewer.init();

	if (!wrapper.value) return;
	resizeObserver = new ResizeObserver(() => viewer.tryResize());
	resizeObserver.observe(document.getElementsByTagName("html")[0]);
});
onUnmounted(() => {
	viewer.destroy();
	if (!wrapper.value || !resizeObserver) return;

	resizeObserver.unobserve(document.getElementsByTagName("html")[0]);
	resizeObserver.disconnect();
});
</script>
<template>
	<div class="pdf-wrapper" ref="wrapper">
		<Transition name="fade" mode="out-in">
			<div v-if="viewer.ready" class="viewer-container" ref="container">
				<div id="viewer" class="pdfViewer"></div>
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
	position: relative;

	width: 100%;
	height: 480px;

	.viewer-container {
		position: absolute;
	}

	.spinner-wrapper {
		display: flex;
		justify-content: center;
		align-items: center;
		position: absolute;

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
