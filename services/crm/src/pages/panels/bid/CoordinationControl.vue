<script setup lang="ts">
import { RowEditor } from "@/hooks/rowEditorHook";
import DefaultButton from "@/components/UI-new/DefaultButton.vue";
import { PropType } from "vue";
import { BidSchema } from "@/types";

const props = defineProps({
	editor: {
		type: Object as PropType<RowEditor<BidSchema>>,
		required: true,
	},
});
const editor = props.editor;

const accept = async () => {
	if (editor.modelIndex.value === undefined) {
		throw Error("Model index is undefined");
	}
	await editor.table.approve(editor.modelIndex.value, true);
	editor.close();
};

const decline = async () => {
	if (editor.modelIndex.value === undefined) {
		throw Error("Model index is undefined");
	}
	await editor.table.reject(editor.modelIndex.value, true, "");
	editor.close();
};
</script>

<template>
	<div class="cc-wrapper">
		<DefaultButton
			class="decline"
			@click="decline"
			title="Отказать"
		></DefaultButton>
		<DefaultButton
			class="accept"
			@click="accept"
			title="Согласовать"
		></DefaultButton>
	</div>
</template>

<style scoped lang="scss">
.cc-wrapper {
	display: flex;
	flex-direction: row;
	justify-content: space-between;

	gap: 27px;

	.decline {
		background-color: $sec-arrantion-red;
	}

	.accept {
		background-color: $stroke-green;
	}
}
</style>
