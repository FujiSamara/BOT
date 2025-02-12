<script setup lang="ts">
import { InputSelectEntity } from ".";
import { PropType } from "vue";
import { computed } from "@vue/reactivity";
import MultiSelectInput from "@/components/selects/MultiSelectInput.vue";

const props = defineProps({
	entity: {
		type: Object as PropType<InputSelectEntity<any>>,
		required: true,
	},
});
const entity = props.entity;

const error = computed(() => {
	if (entity.error.value) {
		return entity.error.value;
	}

	if (
		entity.formattedField.value.length &&
		entity.formattedField.value.length < entity.neededWord
	) {
		return "";
	}
	if (entity.notFound.value) {
		return "";
	}

	return undefined;
});
</script>

<template>
	<div class="e-select">
		<span v-if="entity.withTitle" class="title">{{ entity.placeholder }}</span>
		<MultiSelectInput
			:error="error"
			:placeholder="entity.placeholder"
			:searchList="entity.entitiesList.value"
			:search-value="entity.formattedField.value"
			:readonly="entity.readonly"
			@submit="(val) => (entity.formattedField.value = val)"
			@select="(index: number) => entity.select(index)"
		></MultiSelectInput>
	</div>
</template>

<style scoped lang="scss">
@import "@/components/entity/entity.scss";
</style>
