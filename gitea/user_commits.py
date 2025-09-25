import requests
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import gitea_settings

# ===== 配置 =====
GITEA_BASE_URL = gitea_settings.gitea_base_url
API_TOKEN = gitea_settings.gitea_api_token
AUTHOR_NAME = gitea_settings.gitea_author_name
AUTHOR_EMAIL = gitea_settings.gitea_author_email


def fetch_user_forked_repositories(username=None, per_page=100):
    """获取用户fork的仓库（更高效）"""
    repositories = []
    
    # 如果没有指定用户名，获取当前认证用户的仓库
    if username:
        url = f"{GITEA_BASE_URL}/api/v1/users/{username}/repos"
    else:
        url = f"{GITEA_BASE_URL}/api/v1/user/repos"
    
    headers = {"Authorization": f"token {API_TOKEN}", "Accept": "application/json"}
    
    page = 1
    while True:
        # 增加每页数量，减少请求次数
        params = {"limit": per_page, "page": page}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ 获取仓库列表失败: {e}")
            if "resp" in locals() and resp is not None:
                print("返回内容:", resp.text)
            break
        
        data = resp.json()
        if not data:
            break
        
        # 只收集fork的仓库
        forked_repos = [repo for repo in data if repo.get('fork', False)]
        repositories.extend(forked_repos)
        
        # 如果这一页没有更多数据，停止分页
        if len(data) < per_page:
            break
            
        page += 1
    
    return repositories


def search_commits_by_author(author_email=None, author_name=None, days=None):
    """尝试使用Gitea搜索API直接查询用户提交（如果支持）"""
    # 构建搜索查询
    search_query = ""
    if author_email:
        search_query = f"author:{author_email}"
    elif author_name:
        search_query = f"author:{author_name}"
    else:
        return None
    
    # 添加时间范围（如果支持）
    if days is not None:
        now = datetime.now(timezone.utc)
        if days == 0:
            # 今天
            date_str = now.strftime("%Y-%m-%d")
            search_query += f" date:{date_str}"
        else:
            # 最近N天
            start_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")
            search_query += f" date:>={start_date}"
    
    url = f"{GITEA_BASE_URL}/api/v1/repos/search"
    headers = {"Authorization": f"token {API_TOKEN}", "Accept": "application/json"}
    
    # 尝试搜索（某些Gitea版本可能不支持commit搜索）
    params = {"q": search_query, "limit": 100}
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code == 200:
            print(f"✅ 使用搜索API查询: {search_query}")
            return resp.json()
        else:
            print(f"⚠️ 搜索API不可用 (状态码: {resp.status_code})，回退到仓库遍历")
            return None
    except requests.RequestException as e:
        print(f"⚠️ 搜索API请求失败: {e}，回退到仓库遍历")
        return None


def fetch_repository_commits(owner, repo, branch="main", author_email=None, author_name=None, per_page=100, max_pages=5):
    """获取指定仓库的提交记录（优化版本）"""
    commits = []
    url = f"{GITEA_BASE_URL}/api/v1/repos/{owner.strip()}/{repo.strip()}/commits"
    headers = {"Authorization": f"token {API_TOKEN}", "Accept": "application/json"}
    
    page = 1
    consecutive_empty_pages = 0
    
    while page <= max_pages:  # 限制最大页数，避免无限查询
        params = {"sha": branch, "limit": per_page, "page": page}
        
        # 如果指定了作者，添加作者过滤参数（某些Gitea版本支持）
        if author_email:
            params["author"] = author_email
        
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"⚠️ 获取仓库 {owner}/{repo} 的提交失败: {e}")
            break
        
        data = resp.json()
        if not data:
            break
        
        # 在客户端过滤作者（如果API不支持服务端过滤）
        filtered_commits = []
        for commit in data:
            commit_info = commit.get("commit", {})
            author_info = commit_info.get("author", {})
            
            name = author_info.get("name")
            email = author_info.get("email")
            
            # 检查是否匹配指定作者
            if author_email and email == author_email:
                filtered_commits.append(commit)
            elif author_name and name == author_name:
                filtered_commits.append(commit)
            elif not author_email and not author_name:
                # 如果没有指定作者，返回所有提交
                filtered_commits.append(commit)
        
        commits.extend(filtered_commits)
        
        # 优化：如果连续几页都没有匹配的提交，提前退出
        if not filtered_commits:
            consecutive_empty_pages += 1
            if consecutive_empty_pages >= 2:  # 连续2页没有匹配，可能后面也没有
                break
        else:
            consecutive_empty_pages = 0
        
        # 如果这一页的数据不满，说明已经到达末尾
        if len(data) < per_page:
            break
        
        page += 1
    
    return commits


def fetch_single_repository_commits(repo_info, author_email, author_name, days):
    """获取单个仓库的提交记录（用于并发执行）"""
    repo_name = repo_info.get("name", "")
    repo_owner = repo_info.get("owner", {}).get("login", "")
    default_branch = repo_info.get("default_branch", "main")
    repo_full_name = f"{repo_owner}/{repo_name}"
    
    try:
        commits = fetch_repository_commits(
            repo_owner, 
            repo_name, 
            default_branch, 
            author_email, 
            author_name,
            per_page=100,
            max_pages=3  # 限制页数，避免单个仓库查询时间过长
        )
        
        # 时间过滤
        if days is not None and commits:
            commits = filter_commits_by_time(commits, days)
        
        return repo_full_name, commits
        
    except Exception as e:
        return repo_full_name, f"ERROR: {e}"


def get_all_user_commits(username=None, author_email=None, author_name=None, days=None, use_concurrent=True):
    """获取用户在所有fork仓库中的提交记录（优化版本）"""
    
    # 首先尝试使用搜索API（如果支持）
    print("🔍 尝试使用搜索API直接查询...")
    search_results = search_commits_by_author(author_email, author_name, days)
    
    if search_results:
        print("✅ 搜索API查询成功！")
        # 这里需要根据实际API响应格式处理搜索结果
        # 注意：Gitea的搜索API主要用于仓库搜索，可能不直接支持提交搜索
        # 如果搜索成功，需要进一步处理结果
    
    # 回退到仓库遍历方法（只查询fork的仓库）
    print("🔍 正在获取用户fork的仓库列表...")
    repositories = fetch_user_forked_repositories(username)
    
    if not repositories:
        print("❌ 没有找到任何fork的仓库")
        return {}
    
    print(f"✅ 找到 {len(repositories)} 个fork仓库（相比于遍历所有仓库，大大减少了查询范围）")
    
    all_commits = defaultdict(list)
    total_commits = 0
    
    if use_concurrent and len(repositories) > 1:
        print("🚀 使用并发查询提高效率...")
        
        # 使用线程池并发查询
        with ThreadPoolExecutor(max_workers=min(5, len(repositories))) as executor:
            # 提交所有任务
            future_to_repo = {
                executor.submit(fetch_single_repository_commits, repo, author_email, author_name, days): repo
                for repo in repositories
            }
            
            # 收集结果
            for i, future in enumerate(as_completed(future_to_repo), 1):
                repo = future_to_repo[future]
                repo_full_name = f"{repo.get('owner', {}).get('login', '')}/{repo.get('name', '')}"
                
                print(f"📂 [{i}/{len(repositories)}] 完成查询: {repo_full_name}")
                
                try:
                    repo_name, commits = future.result()
                    
                    if isinstance(commits, str) and commits.startswith("ERROR:"):
                        print(f"  ❌ 查询失败: {commits}")
                    elif commits:
                        all_commits[repo_name] = commits
                        total_commits += len(commits)
                        print(f"  ✅ 找到 {len(commits)} 条提交记录")
                    else:
                        print(f"  📭 无提交记录")
                        
                except Exception as e:
                    print(f"  ❌ 处理结果失败: {e}")
    else:
        # 顺序查询（用于单个仓库或禁用并发时）
        print("📝 使用顺序查询...")
        for i, repo in enumerate(repositories, 1):
            repo_full_name = f"{repo.get('owner', {}).get('login', '')}/{repo.get('name', '')}"
            print(f"📂 [{i}/{len(repositories)}] 正在检查fork仓库: {repo_full_name}")
            
            repo_name, commits = fetch_single_repository_commits(repo, author_email, author_name, days)
            
            if isinstance(commits, str) and commits.startswith("ERROR:"):
                print(f"  ❌ 查询失败: {commits}")
            elif commits:
                all_commits[repo_name] = commits
                total_commits += len(commits)
                print(f"  ✅ 找到 {len(commits)} 条提交记录")
            else:
                print(f"  📭 无提交记录")
    
    print(f"\n🎯 总计在 {len(all_commits)} 个fork仓库中找到 {total_commits} 条提交记录")
    return all_commits


def filter_commits_by_time(commits, days):
    """根据时间范围过滤提交"""
    if days is None:
        return commits
    
    now = datetime.now(timezone.utc)
    filtered_commits = []
    
    for commit in commits:
        commit_info = commit.get("commit", {})
        author_info = commit_info.get("author", {})
        date_str = author_info.get("date")
        
        try:
            if date_str.endswith("Z"):
                commit_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            elif "+" in date_str or date_str.count("-") > 2:
                commit_date = datetime.fromisoformat(date_str)
            else:
                commit_date = datetime.fromisoformat(date_str)
        except Exception as e:
            print(f"⚠️ 日期解析失败: {date_str}, 错误: {e}")
            continue
        
        if days == 0:  # 今天
            if commit_date.date() == now.date():
                filtered_commits.append(commit)
        else:  # 最近 N 天
            if commit_date >= now - timedelta(days=days):
                filtered_commits.append(commit)
    
    return filtered_commits


def format_date(date_str):
    """格式化日期显示"""
    if not date_str or date_str == "未知":
        return "未知时间"
    
    try:
        if date_str.endswith("Z"):
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(date_str)
        
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return date_str


def print_user_commits_summary(all_commits):
    """打印用户提交记录摘要"""
    if not all_commits:
        print("📭 没有找到任何提交记录")
        return
    
    total_commits = sum(len(commits) for commits in all_commits.values())
    
    print(f"\n📊 提交记录统计")
    print("=" * 80)
    print(f"🎯 涉及仓库数量: {len(all_commits)}")
    print(f"📝 总提交数量: {total_commits}")
    print("=" * 80)
    
    # 按仓库显示统计
    print("\n📂 各仓库提交统计:")
    print("-" * 80)
    
    # 按提交数量排序
    sorted_repos = sorted(all_commits.items(), key=lambda x: len(x[1]), reverse=True)
    
    for repo_name, commits in sorted_repos:
        latest_commit = None
        if commits:
            # 找到最新的提交
            latest_commit = max(
                commits,
                key=lambda c: c.get("commit", {}).get("author", {}).get("date", "")
            )
        
        latest_date = "无"
        if latest_commit:
            commit_info = latest_commit.get("commit", {})
            author_info = commit_info.get("author", {})
            latest_date = format_date(author_info.get("date", ""))
        
        print(f"📁 {repo_name:<40} 📝 {len(commits):>3} 条  📅 最新: {latest_date}")
    
    print("-" * 80)


def print_all_commits_detailed(all_commits):
    """详细显示所有提交记录"""
    if not all_commits:
        print("📭 没有找到任何提交记录")
        return {}
    
    print(f"\n📋 详细提交记录")
    print("=" * 120)
    
    # 收集所有提交并按时间排序
    all_commits_list = []
    for repo_name, commits in all_commits.items():
        for commit in commits:
            commit_with_repo = commit.copy()
            commit_with_repo['_repo_name'] = repo_name
            all_commits_list.append(commit_with_repo)
    
    # 按提交时间倒序排列（最新的在前面）
    sorted_commits = sorted(
        all_commits_list,
        key=lambda c: c.get("commit", {}).get("author", {}).get("date", ""),
        reverse=True,
    )
    
    # 表头
    print(f"{'序号':<4} {'仓库':<25} {'SHA':<8} {'时间':<17} {'提交信息':<45}")
    print("-" * 120)
    
    for i, commit in enumerate(sorted_commits, 1):
        sha = commit.get("sha", "")[:7]
        repo_name = commit.get('_repo_name', '')
        commit_info = commit.get("commit", {})
        message = commit_info.get("message", "").split("\n")[0]
        
        # 截断过长的信息
        if len(repo_name) > 22:
            repo_name = repo_name[:19] + "..."
        if len(message) > 42:
            message = message[:39] + "..."
        
        author_info = commit_info.get("author", {})
        date = format_date(author_info.get("date", "未知时间"))
        
        # 美化时间显示
        if date != "未知时间":
            date = date.split(" ")[0] + " " + date.split(" ")[1][:5]
        
        print(f"{i:2d}.  {repo_name:<25} {sha:<8} {date:<17} {message:<45}")
    
    print("=" * 120)
    return {i: commit for i, commit in enumerate(sorted_commits, 1)}


def show_commit_details_menu(commits_dict):
    """显示commit详情选择菜单"""
    if not commits_dict:
        print("❌ 没有找到提交记录")
        return
    
    while True:
        print(f"\n📋 共找到 {len(commits_dict)} 条提交记录")
        print("请选择操作:")
        print("1. 查看某个commit的详细信息")
        print("2. 返回主菜单")
        
        try:
            detail_choice = input("请输入选项 (1-2): ").strip()
            
            if detail_choice == "1":
                commit_num = int(
                    input(f"请输入要查看的commit编号 (1-{len(commits_dict)}): ").strip()
                )
                if commit_num in commits_dict:
                    selected_commit = commits_dict[commit_num]
                    repo_name = selected_commit.get('_repo_name', '')
                    owner, repo = repo_name.split('/', 1) if '/' in repo_name else ('', repo_name)
                    sha = selected_commit.get("sha", "")
                    
                    print(f"\n⏳ 正在获取commit {sha[:7]} 的详细信息...")
                    commit_details = fetch_commit_details(owner, repo, sha)
                    if commit_details:
                        print_commit_details(commit_details, repo_name)
                else:
                    print(f"❌ 请输入 1-{len(commits_dict)} 之间的数字")
            elif detail_choice == "2":
                break
            else:
                print("❌ 无效选项，请输入 1-2")
        
        except (ValueError, KeyboardInterrupt):
            print("\n👋 返回主菜单")
            break


def fetch_commit_details(owner, repo, sha):
    """获取单个commit的详细信息"""
    possible_urls = [
        f"{GITEA_BASE_URL}/api/v1/repos/{owner.strip()}/{repo.strip()}/git/commits/{sha}",
        f"{GITEA_BASE_URL}/api/v1/repos/{owner.strip()}/{repo.strip()}/commits/{sha}",
    ]
    
    headers = {"Authorization": f"token {API_TOKEN}", "Accept": "application/json"}
    
    for url in possible_urls:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException:
            continue
    
    return None


def print_commit_details(commit_data, repo_name):
    """打印commit的详细信息"""
    if not commit_data:
        print("❌ 无法获取commit详细信息")
        return
    
    print("\n" + "=" * 80)
    print(f"📋 COMMIT 详细信息 - {repo_name}")
    print("=" * 80)
    
    # 基本信息
    sha = commit_data.get("sha", commit_data.get("id", ""))
    
    if "commit" in commit_data:
        commit_info = commit_data.get("commit", {})
        author_info = commit_info.get("author", {})
        committer_info = commit_info.get("committer", {})
    else:
        commit_info = commit_data
        author_info = commit_data.get("author", {})
        committer_info = commit_data.get("committer", {})
    
    print(f"🔗 SHA: {sha}")
    print(f"📂 仓库: {repo_name}")
    
    # 提交信息
    message = commit_info.get("message", "无")
    if "\n" in message:
        lines = message.split("\n")
        print(f"📝 提交信息: {lines[0]}")
        if len(lines) > 1:
            print("📄 详细描述:")
            for line in lines[1:]:
                if line.strip():
                    print(f"    {line}")
    else:
        print(f"📝 提交信息: {message}")
    
    # 作者信息
    author_name = author_info.get("name", "未知")
    author_email = author_info.get("email", "未知")
    author_date = format_date(author_info.get("date", "未知"))
    
    print(f"👤 作者: {author_name} <{author_email}>")
    print(f"📅 提交时间: {author_date}")
    
    # 统计信息
    stats = commit_data.get("stats", {})
    if stats:
        additions = stats.get("additions", 0)
        deletions = stats.get("deletions", 0)
        total = stats.get("total", 0)
        if total > 0:
            print(f"📊 统计: +{additions} 行, -{deletions} 行, {total} 行变更")
    
    # 链接
    html_url = commit_data.get("html_url", "")
    if html_url:
        print(f"🔗 查看链接: {html_url}")
    
    print("=" * 80)


def show_menu():
    """显示菜单选项"""
    print("\n" + "=" * 60)
    print("👤 Gitea 用户提交记录查询工具")
    print(f"👤 查询用户: {AUTHOR_NAME} <{AUTHOR_EMAIL}>")
    print("=" * 60)
    print("请选择要查看的时间范围:")
    print("1. 📅 今天的提交")
    print("2. 📅 最近7天的提交")
    print("3. 📅 最近30天的提交")
    print("4. 📅 所有提交")
    print("5. ⚙️  修改配置")
    print("0. 🚪 退出程序")
    print("-" * 60)


def show_config_menu():
    """显示配置菜单"""
    print("\n" + "=" * 50)
    print("⚙️ 配置管理")
    print("=" * 50)
    print("当前配置:")
    print(f"🔗 Gitea地址: {GITEA_BASE_URL}")
    print(f"👤 用户名: {AUTHOR_NAME}")
    print(f"📧 用户邮箱: {AUTHOR_EMAIL}")
    print("-" * 50)
    print("1. 修改用户邮箱")
    print("2. 修改用户名")
    print("3. 返回主菜单")
    print("-" * 50)


def handle_config_change():
    """处理配置修改"""
    global AUTHOR_EMAIL, AUTHOR_NAME
    
    while True:
        show_config_menu()
        try:
            choice = input("请输入选项 (1-3): ").strip()
            
            if choice == "1":
                new_email = input(
                    f"请输入新的用户邮箱 (当前: {AUTHOR_EMAIL}): "
                ).strip()
                if new_email:
                    AUTHOR_EMAIL = new_email
                    print(f"✅ 用户邮箱已更新为: {AUTHOR_EMAIL}")
            elif choice == "2":
                new_name = input(f"请输入新的用户名 (当前: {AUTHOR_NAME}): ").strip()
                if new_name:
                    AUTHOR_NAME = new_name
                    print(f"✅ 用户名已更新为: {AUTHOR_NAME}")
            elif choice == "3":
                break
            else:
                print("❌ 无效选项，请输入 1-3")
        
        except KeyboardInterrupt:
            print("\n👋 返回主菜单")
            break


def show_startup_banner():
    """显示启动横幅"""
    print("\n" + "=" * 60)
    print("🚀 Gitea 用户提交记录查询工具")
    print("=" * 60)
    print("📋 功能特性:")
    print("  • 👤 查询用户在所有仓库中的提交记录")
    print("  • 📅 按时间范围过滤提交")
    print("  • 📊 显示跨仓库的统计信息")
    print("  • 🔍 查看详细的commit信息")
    print("  • ⚙️  动态配置修改")
    print("=" * 60)
    print(f"🔗 Gitea实例: {GITEA_BASE_URL}")
    print(f"👤 查询用户: {AUTHOR_NAME} <{AUTHOR_EMAIL}>")
    print("=" * 60)


if __name__ == "__main__":
    try:
        show_startup_banner()
        
        while True:
            show_menu()
            try:
                choice = input("请输入选项 (0-5): ").strip()
                
                if choice == "0":
                    print("👋 再见!")
                    break
                elif choice == "1":
                    print("\n===== 今天的提交 =====")
                    all_commits = get_all_user_commits(
                        author_email=AUTHOR_EMAIL,
                        author_name=AUTHOR_NAME,
                        days=0
                    )
                    print_user_commits_summary(all_commits)
                    commits_dict = print_all_commits_detailed(all_commits)
                    show_commit_details_menu(commits_dict)
                elif choice == "2":
                    print("\n===== 最近7天的提交 =====")
                    all_commits = get_all_user_commits(
                        author_email=AUTHOR_EMAIL,
                        author_name=AUTHOR_NAME,
                        days=7
                    )
                    print_user_commits_summary(all_commits)
                    commits_dict = print_all_commits_detailed(all_commits)
                    show_commit_details_menu(commits_dict)
                elif choice == "3":
                    print("\n===== 最近30天的提交 =====")
                    all_commits = get_all_user_commits(
                        author_email=AUTHOR_EMAIL,
                        author_name=AUTHOR_NAME,
                        days=30
                    )
                    print_user_commits_summary(all_commits)
                    commits_dict = print_all_commits_detailed(all_commits)
                    show_commit_details_menu(commits_dict)
                elif choice == "4":
                    print("\n===== 所有提交 =====")
                    all_commits = get_all_user_commits(
                        author_email=AUTHOR_EMAIL,
                        author_name=AUTHOR_NAME,
                        days=None
                    )
                    print_user_commits_summary(all_commits)
                    commits_dict = print_all_commits_detailed(all_commits)
                    show_commit_details_menu(commits_dict)
                elif choice == "5":
                    handle_config_change()
                else:
                    print("❌ 无效选项，请输入 0-5 之间的数字")
            
            except KeyboardInterrupt:
                print("\n\n👋 程序被用户中断，再见!")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
            
            input("\n按回车键继续...")
    
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        print("请检查网络连接和配置信息")
        exit(1)
