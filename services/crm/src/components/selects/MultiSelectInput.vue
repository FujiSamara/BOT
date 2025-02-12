<script setup lang="ts">
import Checkbox from "@/components/UI-new/Checkbox.vue";
import MaybeDelayInput from "@/components/MaybeDelayInput.vue";
import { computed, PropType, ref } from "vue";
import * as animations from "@/components/selects/multiSelectAnimations";

const props = defineProps({
	error: {
		type: String,
	},
	placeholder: {
		type: String,
	},
	searchList: {
		type: Array as PropType<{ checked: boolean; value: string }[]>,
		required: true,
	},
	searchValue: {
		type: String,
		required: true,
	},
	readonly: {
		type: Boolean,
	},
});
const emits = defineEmits<{
	(e: "select", index: number): void;
	(e: "submit", value: string): void;
}>();

const active = ref(false);
const list = computed(() => {
	if (!active.value) {
		return [...props.searchList].filter((val) => val.checked);
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
			:readonly="props.readonly"
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
				class="msi-row-wrapper"
				:key="row.value + (row.checked ? 'c' : 'unc')"
				v-for="(row, index) in list"
				:data-index="index"
			>
				<div class="msi-row">
					{{ row.value }}
				</div>
				<Checkbox :checked="row.checked" @click="emits('select', index)">
				</Checkbox>
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

		.msi-row-wrapper {
			@include field;
			width: inherit;
			height: 48px;
			justify-content: space-between;
			margin-top: 8px;

			.msi-row {
				max-width: 80%;
				overflow-x: hidden;
			}
		}
	}
}
</style>
