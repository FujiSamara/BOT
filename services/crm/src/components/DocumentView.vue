<script setup lang="ts">
import { useNetworkStore } from "@/store/network";
import { DocumentSchema } from "@/types";
import Viewer from "viewerjs";
import { onMounted, ref, Ref, useTemplateRef } from "vue";

const network = useNetworkStore();

const props = defineProps({
	documents: {
		type: Array<DocumentSchema>,
		required: true,
	},
	index: {
		type: Number,
		required: true,
	},
});

const emit = defineEmits(["close"]);

const imageContainer = useTemplateRef("image-container");
const viewer: Ref<Viewer | undefined> = ref();
const viewerOptions: Viewer.Options = {
	button: false,
	scalable: false,
	tooltip: false,
	title: true,
	initialViewIndex: props.index,
	toolbar: {
		flipHorizontal: false,
		flipVertical: false,
		reset: false,
		play: false,
		oneToOne: false,
		prev: true,
		next: true,
		zoomIn: true,
		zoomOut: true,
		rotateLeft: true,
		rotateRight: true,
	},
	hidden: () => emit("close"),
};

const documents: Array<string> = [];
for (const document of props.documents) {
	const documentData = await network.getFile(document.name);

	let type = "application/octet-stream";
	let extension = document.name.split(".").reverse()[0];
	if (extension === "svg") {
		type = "image/svg+xml";
	}
	const blob = new Blob([documentData], {
		type: type,
	});

	documents.push(window.URL.createObjectURL(blob));
}

onMounted(() => {
	viewer.value = new Viewer(imageContainer.value!, viewerOptions);
	viewer.value.show();
});
</script>

<template>
	<div class="wrapper" ref="image-container">
		<img
			v-for="(document, index) in documents"
			v-show="false"
			:src="document"
			:key="document"
			:alt="props.documents[index].name"
		/>
	</div>
</template>

<style scoped>
.view {
	width: 720px;
	height: 480px;
	padding: 10px;
}
.layout {
	background-size: cover;
	width: 100%;
	height: 100%;
}
</style>
