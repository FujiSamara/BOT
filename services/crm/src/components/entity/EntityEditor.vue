<script setup lang="ts">
import BlurModal from "@/components/BlurModal.vue";
import { EditorMode, BaseEntityEditor } from "@/hooks/entityEditorHook";
import { PropType } from "vue";
import EntitySelect from "../entity/EntitySelect.vue";
import DefaultButton from "../UI-new/DefaultButton.vue";

const props = defineProps({
	editor: {
		type: Object as PropType<BaseEntityEditor>,
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
	<Transition name="fade">
		<BlurModal
			:title="editor.title.value"
			v-if="editor.active.value"
			@close="editor.close"
			class="modal"
		>
			<div class="e-selects">
				<EntitySelect
					v-for="field in editor.fields.filter((val) => val.active)"
					:entity="field.entity"
					:select-type="field.type"
					class="select-wrapper"
					v-if="!editor.showCustom.value"
				></EntitySelect>
				<DefaultButton
					v-if="
						editor.mode.value !== EditorMode.View && !editor.showCustom.value
					"
					@click="save"
					title="Сохранить"
				></DefaultButton>
				<slot name="view"></slot>
				<slot name="create"></slot>
				<slot name="edit"></slot>
			</div>
		</BlurModal>
	</Transition>
</template>

<style scoped lang="scss">
.e-selects {
	display: flex;
	flex-direction: column;
	min-width: fit-content;

	:not(:nth-child(1)).select-wrapper {
		margin-top: 24px;
	}
	:nth-last-child(2).select-wrapper {
		margin-bottom: 24px;
	}

	overflow-y: auto;
}
</style>
