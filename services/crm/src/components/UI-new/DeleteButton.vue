<script setup lang="ts">
import DefaultButton from "./DefaultButton.vue";

const props = defineProps({
	disabled: {
		type: Boolean,
	},
});

const emits = defineEmits(["click"]);
</script>

<template>
	<DefaultButton
		class="delete-button"
		:title="''"
		:disabled="props.disabled"
		@click="emits('click')"
	>
		<div class="tool-icon-wrapper">
			<div class="tool-icon bin"></div>
		</div>
	</DefaultButton>
</template>

<style scoped lang="scss">
.delete-button {
	@include withIcon();

	min-width: 110px;
	max-width: 110px;
	width: 110px;
	max-height: 100%;

	flex-grow: 1;

	background-color: $sec-arrantion-red;

	.tool-icon-wrapper {
		height: 16px;
		width: 16px;
		.tool-icon {
			color: $main-white;
			width: 9px;
			height: 10px;

			&.bin {
				mask-image: url("@/assets/icons/bin.svg");
			}
		}
	}
}
</style>
