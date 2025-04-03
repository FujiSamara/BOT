<script setup lang="ts">
import { nextTick, PropType, ref, useTemplateRef } from "vue";
import PDFView from "@/components/PDFView.vue";
import { FileLinkSchema } from "@/components/knowledge";

const props = defineProps({
	file: {
		type: Object as PropType<FileLinkSchema>,
		required: true,
	},
});

const pdfExpanded = ref(false);
const pdfRef = useTemplateRef("pdf");

const expand = async () => {
	if (!pdfRef.value) return;

	pdfExpanded.value = !pdfExpanded.value;
	if (pdfExpanded.value) {
		const element = pdfRef.value.$el as HTMLElement;
		element.style.height = `${pdfRef.value.actualHeight}px`;
	} else {
		const element = pdfRef.value.$el as HTMLElement;
		element.style.height = "480px";
	}

	await nextTick();

	await pdfRef.value.renderPage();
};
</script>
<template>
	<div class="document-wrapper">
		<PDFView class="pdf" ref="pdf" :file="props.file"></PDFView>
		<div class="expand" @click="expand">
			<span>{{ pdfExpanded ? "Свернуть" : "Развернуть" }}</span>
			<span class="icon" :class="{ reversed: pdfExpanded }"></span>
		</div>
	</div>
</template>
<style scoped lang="scss">
.document-wrapper {
	display: flex;
	flex-direction: column;
	align-items: center;

	gap: 16px;

	width: 100%;
	height: fit-content;

	.pdf {
		width: 100%;
		height: 480px;

		border-radius: 16px;
	}

	.expand {
		display: flex;
		flex-direction: row;
		align-items: center;

		gap: 10px;

		cursor: pointer;
		color: $main-dark-gray;

		span {
			position: relative;
			display: inline-block;

			font-family: Wix Madefor Display;
			font-weight: 500;
			font-size: 16px;

			&::after {
				content: "";
				position: absolute;
				left: 0;
				bottom: 0;
				opacity: 0;
				height: 1px;
				width: 100%;
				background-color: currentColor;
				transition: opacity 0.25s;
			}
		}

		&:hover span::after {
			opacity: 1;
		}

		.icon {
			@include arrow();

			transition:
				transform 0.25s,
				opacity 0.5s ease;
		}
	}
}
</style>
