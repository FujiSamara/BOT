<script setup lang="ts">
import { PropType } from "vue";
import { computed } from "@vue/reactivity";
import { InputEntity } from "@/components/entity";
import MaybeDelayInput from "@/components/MaybeDelayInput.vue";

const props = defineProps({
	entity: {
		type: Object as PropType<InputEntity<any>>,
		required: true,
	},
});
const entity = props.entity;

const error = computed(() => {
	if (entity.error.value) {
		return entity.error.value;
	}
});
</script>

<template>
	<div class="e-select">
		<span v-if="entity.withTitle" class="title">{{ entity.placeholder }}</span>
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
			:readonly="entity.readonly"
		></MaybeDelayInput>
	</div>
</template>

<style scoped lang="scss">
@import "@/components/entity/entity.scss";

.msi-input {
	flex-grow: 1;
	height: 48px;
}
</style>
