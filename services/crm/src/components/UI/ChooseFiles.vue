<template>
	<div class="wrapper">
		<input type="file" multiple ref="input" @change.prevent="onChange" />
		<div class="add-files">
			<clickable-icon
				class="icons"
				img-src="/img/add-plus.svg"
				@click="input!.click()"
			></clickable-icon>
			<span>Добавить файлы</span>
		</div>
		<transition-group tag="ul" name="files">
			<li v-for="(file, index) in files" :key="index">
				<span>{{ file.name }}</span>
				<window-cross
					class="cross"
					@click="() => onDelete(index)"
				></window-cross>
			</li>
		</transition-group>
	</div>
</template>
<script setup lang="ts">
import { Ref, useTemplateRef } from "vue";

const input = useTemplateRef("input");
const files: Ref<Array<File>> = defineModel("files", {
	required: true,
	type: Array<File>,
});

const onDelete = (index: number) => {
	files.value.splice(index, 1);
};

const onChange = (event: Event) => {
	const target = event.target as HTMLInputElement;
	files.value.push(...target.files!);
	target.value = "";

	// emit("change", Array.from(target.files!));
};
</script>
<script lang="ts">
export default {
	name: "choose-files",
};
</script>
<style scoped>
.wrapper {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	justify-content: center;
	gap: 10px;
}
.add-files {
	display: flex;
	flex-direction: row;
	align-items: center;
	gap: 10px;
}
.icons {
	width: 20px;
}
ul {
	list-style: none;
	color: #993ca6;

	margin: 0;
	padding: 0;
	display: flex;
	flex-direction: column;
	align-items: flex-start;
}

li {
	display: flex;
	flex-direction: row;
	align-items: center;
	gap: 10px;
}

li .cross {
	height: 16px;
	width: 16px;
}

input[type="file"] {
	width: 0;
	overflow: hidden;
	opacity: 0;
	display: inline;
	position: absolute;
}

.files-enter-active,
.files-leave-active {
	transition: all 0.5s ease;
}

.files-enter-from,
.files-leave-to {
	opacity: 0;
}
</style>
