<script setup lang="ts">
import BlurModal from "@/components/BlurModal.vue";
import { RowEditor } from "@/hooks/rowEditorHook";
import { PropType } from "vue";
import EntitySelect from "../entity/EntitySelect.vue";

const props = defineProps({
	editor: {
		type: Object as PropType<RowEditor>,
		required: true,
	},
});
const editor = props.editor;
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
	</BlurModal>
</template>

<style scoped lang="scss"></style>
