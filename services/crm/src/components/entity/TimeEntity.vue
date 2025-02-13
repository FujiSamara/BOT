<script setup lang="ts">
import { computed, PropType, ref } from "vue";
import { DateEntity } from "@/components/entity";
import TimeSelectInput from "@/components/selects/TimeSelectInput.vue";

const props = defineProps({
	entity: {
		type: Object as PropType<DateEntity>,
		required: true,
	},
});
const entity = props.entity;

const emits = defineEmits<{
	(e: "submit", value: string): void;
	(e: "close"): void;
}>();

const active = ref(false);

const focusOut = () => {
	active.value = false;

	emits("close");
};

const error = computed(() => {
	if (entity.error.value) {
		return entity.error.value;
	}
	return undefined;
});
</script>

<template>
	<div class="e-select">
		<span v-if="entity.withTitle" class="title">{{ entity.placeholder }}</span>
		<TimeSelectInput
			:required="entity.required"
			:placeholder="entity.placeholder"
			:value="entity.formattedField.value"
			:error="error"
			@submit="(val) => (entity.formattedField.value = val)"
			@close="focusOut"
			:readonly="entity.readonly"
		></TimeSelectInput>
	</div>
</template>

<style scoped lang="scss">
@import "@/components/entity/entity.scss";

.msi-wrapper {
	display: flex;
	flex-direction: column;
	position: relative;
	flex-grow: 1;

	.msi-input {
		width: 100%;
		height: 48px;
	}
}
</style>
