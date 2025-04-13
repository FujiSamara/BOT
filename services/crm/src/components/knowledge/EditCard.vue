<script setup lang="ts">
import { PropType } from "vue";
import EntitySelect from "@/components/entity/EntitySelect.vue";
import DefaultButton from "@/components/UI-new/DefaultButton.vue";

import { Field } from "@/components/knowledge/editor";

const props = defineProps({
	fields: {
		type: Array as PropType<Field[]>,
		required: true,
	},
});

const fields = props.fields;

const emits = defineEmits<{
	(e: "save", fields: Field[]): void;
}>();
</script>
<template>
	<div class="e-selects">
		<EntitySelect
			v-for="field in fields"
			:entity="field.entity"
			:select-type="field.type"
			class="select-wrapper"
		></EntitySelect>
		<DefaultButton
			@click="emits('save', fields)"
			title="Сохранить"
		></DefaultButton>
	</div>
</template>
<style scoped lang="scss">
.e-selects {
	display: flex;
	flex-direction: column;
	min-width: fit-content;

	:not(:nth-child(1)).select-wrapper {
		margin-top: 32px;
	}
	:nth-last-child(2).select-wrapper {
		margin-bottom: 32px;
	}

	overflow-y: auto;
}
</style>
