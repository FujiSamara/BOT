<script setup lang="ts">
const props = defineProps({
	title: {
		type: String,
		required: true,
	},
});

const emits = defineEmits(["click"]);
</script>

<template>
	<button>
		<span>
			{{ props.title }}
		</span>
	</button>
</template>

<style scoped lang="scss">
button {
	display: flex;
	justify-content: center;
	align-items: center;

	height: 42px;
	width: 100%;

	border-radius: 8px;
	border: 1px solid transparent;
	padding: 16px 20px;
	background-color: $main-dark-gray;

	&:hover {
		cursor: pointer;
		opacity: 0.95;
	}

	span {
		font-family: Wix Madefor Display;
		font-size: 14px;
		font-weight: 500;
		line-height: 17.64px;
		color: $main-white;
	}

	transition: opacity 0.25s;
}
</style>
