<script setup lang="ts">
const props = defineProps({
	short: {
		type: Boolean,
		required: false,
	},
});
</script>

<template>
	<div class="fuji-header">
		<Transition name="fade">
			<div v-if="!props.short" class="logo"></div>
		</Transition>
		<Transition name="fade">
			<div v-if="props.short" class="logo short"></div>
		</Transition>
	</div>
</template>

<style scoped lang="scss">
.fuji-header {
	display: flex;
	flex-direction: row;
	justify-content: center;

	height: 31px;

	.logo {
		background-color: currentColor;
		color: $logo-color;
		width: 153px;
		height: 31px;
		fill: currentColor;

		mask-image: url("@/assets/icons/logo.svg");
		mask-size: contain;
		mask-repeat: no-repeat;

		position: absolute;

		&.short {
			width: 30.56px;
			height: 31px;
			mask-image: url("@/assets/icons/logo-short.svg");
		}
	}
}
</style>
