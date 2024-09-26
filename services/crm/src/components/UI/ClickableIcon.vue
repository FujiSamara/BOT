<template>
	<div class="button-wrapper" @click.prevent>
		<img :src="props.imgSrc" :class="{ filtered: props.withFilter }" />
	</div>
</template>
<script setup lang="ts">
const props = defineProps({
	imgSrc: {
		type: String,
		required: true,
	},
	withFilter: {
		type: Boolean,
		default: true,
	},
});
</script>
<script lang="ts">
export default {
	name: "clickable-icon",
};
</script>
<style scoped>
.button-wrapper {
	display: flex;
	align-items: center;
	justify-content: center;
	flex-direction: column;
	cursor: pointer;
	user-select: none;
	transition: 0.5s;
	-webkit-transition: 0.5s;
}
.button-wrapper:hover {
	transition: 0.5s;
	-webkit-transition: 0.5s;
	transform: scale(1.1);
}
.button-wrapper p {
	font-size: 18px;
	font-family: Stolzl;
	font-weight: 400;
	margin: 0;
	color: #cccccc;
}
.button-wrapper img {
	width: 100%;
	height: 100%;
}
.filtered {
	filter: brightness(0) saturate(100%) invert(32%) sepia(12%) saturate(6808%)
		hue-rotate(262deg) brightness(93%) contrast(90%);
}
</style>
