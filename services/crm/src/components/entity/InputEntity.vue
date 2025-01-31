<script setup lang="ts">
import { PropType } from "vue";
import { computed } from "@vue/reactivity";
import { ValidatingInputEntity } from "@/components/entity";
import MaybeDelayInput from "@/components/MaybeDelayInput.vue";

const props = defineProps({
	entity: {
		type: Object as PropType<ValidatingInputEntity<any>>,
		required: true,
	},
});
const entity = props.entity;

const error = computed(() => {
	if (!entity.validatingResult.value) {
		return undefined;
	}

	return entity.validatingResult.value;
});
</script>

<template>
	<div class="e-select">
		<MaybeDelayInput
			class="msi-input"
			:value="entity.formattedField.value"
			@submit="(val) => (entity.formattedField.value = val)"
			:error="error"
			:placeholder="entity.placeholder"
			:with-search-icon="false"
			:with-edit-mark="true"
			:error-left-align="true"
			:required="entity.required"
		></MaybeDelayInput>
	</div>
</template>

<style scoped lang="scss">
.msi-input {
	width: 100%;
	height: 48px;
}
</style>
