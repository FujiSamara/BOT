<script setup lang="ts">
import MaybeDelayInput from "@/components/MaybeDelayInput.vue";
import { computed, ref } from "vue";

const props = defineProps({
	error: {
		type: String,
	},
	disabled: {
		type: Boolean,
	},
	placeholder: {
		type: String,
	},
	value: {
		type: String,
		required: true,
	},
	required: {
		type: Boolean,
		default: false,
	},
});
const emits = defineEmits<{
	(e: "submit", value: string): void;
	(e: "close"): void;
}>();

const active = ref(false);
const value = computed(() => {
	if (!props.value) {
		return "";
	}
	return props.value;
});

const focusOut = () => {
	active.value = false;

	emits("close");
};
</script>

<template>
	<div class="tsi-wrapper" @focusin="active = true" @focusout="focusOut">
		<MaybeDelayInput
			class="msi-input"
			:value="value"
			@submit="(val: string) => emits('submit', val)"
			:error="props.error"
			:placeholder="props.placeholder"
			:with-search-icon="false"
			:with-edit-mark="true"
			:error-left-align="true"
			:required="props.required"
			:disabled="props.disabled"
		></MaybeDelayInput>
	</div>
</template>

<style scoped lang="scss">
.tsi-wrapper {
	display: flex;
	flex-direction: column;
	position: relative;

	.msi-input {
		width: 100%;
		height: 48px;
	}
}
</style>
