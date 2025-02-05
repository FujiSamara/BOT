<script setup lang="ts">
import BlurModal from "@/components/BlurModal.vue";
import { RowEditor } from "@/hooks/rowEditorHook";
import { PropType } from "vue";
import EntitySelect from "../entity/EntitySelect.vue";
import DefaultButton from "../UI-new/DefaultButton.vue";

const props = defineProps({
	editor: {
		type: Object as PropType<RowEditor>,
		required: true,
	},
});
const editor = props.editor;

const save = () => {
	let ready = true;

	for (const field of editor.fields) {
		const entiy = field.entity;

		if (!entiy.completed.value && entiy.required) {
			ready = false;

			const currentError = entiy.overrideError.value;

			entiy.overrideError.value = "Обязательное поле";

			setTimeout(() => {
				entiy.overrideError.value = currentError;
			}, 2000);
		}

		if (entiy.error.value) {
			ready = false;
		}
	}

	if (ready) {
		editor.save();
	}
};
</script>

<template>
	<BlurModal
		:title="editor.title.value"
		v-if="editor.active.value"
		@close="editor.close"
	>
		<EntitySelect
			v-for="field in editor.fields"
			:entity="field.entity"
			:select-type="field.type"
		></EntitySelect>
		<DefaultButton @click="save" title="Сохранить"></DefaultButton>
	</BlurModal>
</template>

<style scoped lang="scss"></style>
