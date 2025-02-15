<script setup lang="ts">
import { InputSelectEntity } from ".";
import { PropType } from "vue";
import { computed } from "@vue/reactivity";
import MonoSelectInput from "@/components/selects/MonoSelectInput.vue";

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
		entity.formattedField.value.length < entity.neededLetter
	) {
		return `Необходимо минимум ${entity.neededLetter} символа`;
	}
	if (entity.notFound.value) {
		return "Совпадения не найдены";
	}

	return undefined;
});
</script>

<template>
	<div class="e-select">
		<span v-if="entity.withTitle" class="title">{{ entity.placeholder }}</span>
		<MonoSelectInput
			:error="error"
			:placeholder="entity.placeholder"
			:searchList="entity.entitiesList.value.map((val) => val.value)"
			:search-value="entity.formattedField.value"
			@submit="(val) => (entity.formattedField.value = val)"
			@select="(index: number) => entity.select(index)"
			@close="() => entity.restoreSaved()"
			:required="entity.required"
			:readonly="entity.readonly"
		>
		</MonoSelectInput>
	</div>
</template>

<style scoped lang="scss">
@import "@/components/entity/entity.scss";
</style>
