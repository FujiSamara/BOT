<script setup lang="ts">
import MaybeDelayInput from "@/components/MaybeDelayInput.vue";
import { computed, PropType, ref } from "vue";
import * as animations from "@/components/selects/monoSelectAnimations";

const props = defineProps({
	error: {
		type: String,
	},
	placeholder: {
		type: String,
	},
	searchList: {
		type: Array as PropType<string[]>,
		required: true,
	},
	searchValue: {
		type: String,
		required: true,
	},
	required: {
		type: Boolean,
		default: false,
	},
});
const emits = defineEmits<{
	(e: "select", index: number): void;
	(e: "submit", value: string): void;
}>();

const active = ref(false);
const list = computed(() => {
	if (!active.value) {
		return [];
	}
	return props.searchList;
});
</script>

<template>
	<div class="msi-wrapper" @focusin="active = true" @focusout="active = false">
		<MaybeDelayInput
			class="msi-input"
			:value="searchValue"
			@submit="(val: string) => emits('submit', val)"
			:error="props.error"
			:placeholder="props.placeholder"
			:with-search-icon="false"
			:with-edit-mark="true"
			:required="props.required"
		></MaybeDelayInput>
		<TransitionGroup
			:css="false"
			tag="ul"
			class="msi-list"
			@before-enter="animations.onBeforeEnter"
			@enter="animations.onEnter"
			@leave="animations.onLeave"
			@pointerdown.prevent
		>
			<li
				class="msi-row"
				:key="row"
				v-for="(row, index) in list"
				:data-index="index"
			>
				{{ row }}
			</li>
		</TransitionGroup>
	</div>
</template>

<style scoped lang="scss">
.msi-wrapper {
	display: flex;
	flex-direction: column;

	.msi-input {
		width: 100%;
		height: 48px;
	}

	.msi-list {
		display: flex;
		flex-direction: column;

		width: 100%;
		padding: 0;
		margin: 0;

		.msi-row {
			margin-top: 8px;
			height: 48px;
		}

		transition: margin-top 0.25s;
	}
}
</style>
