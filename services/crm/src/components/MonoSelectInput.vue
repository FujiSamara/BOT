<script setup lang="ts">
import SearchInput from "@/components/SearchInput.vue";
import { computed, PropType, ref } from "vue";
import * as animations from "@/components/entity/animations";

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
		<SearchInput
			class="msi-input"
			:value="searchValue"
			@submit="(val: string) => emits('submit', val)"
			:error="props.error"
			:placeholder="props.placeholder"
		></SearchInput>
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
	gap: 16px;

	.msi-input {
		width: 100%;
	}

	.msi-list {
		display: flex;
		flex-direction: column;
		gap: 10px;

		width: 100%;
		padding: 0;

		.msi-row {
		}

		&:empty {
			margin-top: calc(-16px);
		}
	}
}
</style>
