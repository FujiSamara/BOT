<template>
	<div class="search-tool-wrapper">
		<input
			:id="props.id"
			:placeholder="props.placeholder"
			@input.prevent="onInput"
		/>
		<img src="/img/search.svg" />
	</div>
</template>
<script setup lang="ts">
const props = defineProps({
	id: {
		type: String,
		required: true,
	},
	placeholder: {
		type: String,
		default: "Поиск",
	},
});
const emit = defineEmits<{
	(e: "input", value: string): void;
}>();

let delaySetter: number = setTimeout(() => {}, 0);
const delay = 500;

const onInput = (event: Event) => {
	const val = (event.target as HTMLInputElement).value;
	clearTimeout(delaySetter);
	delaySetter = setTimeout(async () => {
		emit("input", val);
	}, delay);
};
</script>
<style scoped>
.search-tool-wrapper {
	display: flex;
	flex-direction: row;
}

input {
	border: none;
	outline: none;
	font-family: Stolzl;
	font-size: 18px;
	color: #7f7f7f;
	width: 170px;
	caret-color: transparent;
}
</style>
